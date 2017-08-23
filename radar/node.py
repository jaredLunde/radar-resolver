import json
from vital.debug import preprX, colorize, bold

from radar.fields import Field, Obj
from radar.exceptions import FieldNotFound, NodeKeyError, NodeIsNull
from radar.members import Members
from radar.interface import Interface
from radar.utils import to_js_keys, transform_keys, to_js_shape


JS_TPL = '''import {{createNode}} from 'react-radar'{imports}


export default createNode({{
  name: '{name}',
  implements: {interfaces},
  fields: {shape}
}})'''


class Node(Interface):

    def __init__(self, callback=None, many=False):
        """ @many: will return #list if @many is |True|
        """
        self.implements = [] if not hasattr(self, 'implements') else\
                          self.implements
        self._key = None
        self.callback = callback
        self.many = many
        self._transform_keys = True
        super().__init__()

    __repr__ = preprX('__NAME__', 'fields', address=False)

    def _compile(self):
        """ Sets :class:Field attributes """
        super()._compile()
        self.implement(*self.implements)

        if self._key is None:
            raise NodeKeyError(f'Node `{self.__NAME__}` does not have a '
                                 'designated key but requires one.')

    def transform_keys(self, truthy_falsy=None):
        self._transform_keys = True if truthy_falsy is None else truthy_falsy

    def add_field(self, field_name, field):
        super().add_field(field_name, field)
        field = self._fields[-1]

        if isinstance(field, Field) and field.key is True:
            self._key = field

    def implement(self, *interfaces):
        for interface_cls in interfaces:
            interface = interface_cls()

            if interface_cls not in self.implements:
                self.implements.append(interface_cls)

            for field in interface.fields:
                self.add_field(field.__NAME__, field)

        return self

    @property
    def key(self):
        if self._key.value is not None:
            return self._key.value

        raise NodeKeyError(f'Node `{self.__NAME__}` did not have a Key field '
                           'with a value. Your Key field cannot ever return '
                           'None.')

    def get_field(self, field_name):
        field = getattr(self, field_name)

        if isinstance(field, (Field, Node)):
            return field

        raise FieldNotFound(f'Field named `{field_name}` was not found in '
                            f'Node `{self.__NAME__}`')

    def get_required_field(self, field, child_fields=None):
        fields = {}
        if isinstance(field, Node):
            fields[field.__NAME__] = field.get_required_fields(child_fields)
        elif isinstance(field, Obj):
            fields[field.__NAME__] = {
                _field.__NAME__: self.get_required_field(
                    _field,
                    child_fields[_field.__NAME__] if child_fields else None
                )
                for _field in field.fields
                if child_fields and _field.__NAME__ in child_fields
            }
        else:
            fields[field.__NAME__] = None

        return fields

    def get_required_fields(self, input_fields=None):
        fields = {}

        if input_fields is None or not len(input_fields):
            for field in self._fields:
                fields.update(self.get_required_field(field))
        else:
            for field_name, child_fields in input_fields.items():
                field_name = self.transform(field_name, False)
                field = self.get_field(field_name)
                required_fields = self.get_required_field(field, child_fields)
                fields.update(required_fields)

        return fields

    def resolve_field(self, query, field_name, sub_fields=None, **data):
        field = self.get_field(self.transform(field_name, False))


        if isinstance(field, Node):
            field = field.copy()
            try:
                return field.copy().resolve(
                    query=query,
                    node=self,
                    fields=sub_fields,
                    **data
                )
            except NodeIsNull:
                return None
        else:
            if sub_fields is None:
                return field.resolve(
                    query=query,
                    node=self,
                    fields=None,
                    **data
                )

            return field.resolve(
                query=query,
                node=self,
                fields=sub_fields,
                **data
            )

    def transform(self, field_name, to_js=True):
        return transform_keys(field_name, self._transform_keys, to_js)

    def resolve_fields(self, query, fields, **data):
        if fields:
            for field_name, sub_fields in fields.items():
                if sub_fields is not None:
                    yield (field_name,
                           self.resolve_field(query, field_name, sub_fields, **data))
                else:
                    yield (field_name,
                           self.resolve_field(query, field_name, **data))
        else:
            for field in self._fields:
                yield (field.__NAME__,
                       self.resolve_field(query, field.__NAME__, **data))

    def _resolve(self, query, fields, index=None, **data):
        data = self.apply(query, fields, index=index, **data) or {}
        out = {
            self.transform(name): value
            for name, value in self.resolve_fields(
                query,
                fields,
                index=index,
                **data
             )
        }

        if self._key.__NAME__ not in fields:
            self.resolve_field(query, self._key.__NAME__, index=index, **data)

        out['@key'] = self.key
        print(f'\n\n{colorize("[𝚁𝙴𝚂𝙾𝙻𝚅𝙴𝙳]", "green")}\n{colorize(query.__NAME__)} -> {bold(self.__NAME__)}',
              json.dumps(out, indent=2))
        try:
            return self.callback(self, out)
        except TypeError:
            return out

    def _resolve_many(self, query, fields, index=None, **data):
        index = 0
        out = []
        append_out = out.append
        for node in self:
            try:
                append_out(
                    node.copy()._resolve(
                        query,
                        fields,
                        index=index,
                        **data
                    )
                )
            except IndexError:
                break
            index += 1

        return out

    def resolve(self, query, fields, index=None, **data):
        self.transform_keys(query._transform_keys)

        if self.many:
            resolver = self._resolve_many
        else:
            resolver = self._resolve

        return resolver(query, fields, index=index, **data)

    def clear(self):
        for field in self._fields:
            field.clear()

        return self

    def apply(self, query, fields, index=None, **data):
        return data

    def copy(self):
        cls = self.__class__(callback=self.callback, many=self.many)
        return cls

    def to_js(self, indent=2, plugins=None):
        shape = {}

        interface_fields = set()
        interface_names = []

        for interface_cls in self.implements:
            interface = interface_cls()
            interface_fields = interface_fields.union(
                set(field.__NAME__ for field in interface.fields)
            )
            interface_names.append(interface.__NAME__)

        nodes = [node for node in self.fields if isinstance(node, Node)]

        for field in self._fields:
            if isinstance(field, Node):
                shape[self.transform(field.__NAME__)] =\
                    f'{field.__class__.__name__}.fields'
            elif field.__NAME__ not in interface_fields:
                if isinstance(field, Obj):
                    # TODO
                    shape[self.transform(field.__NAME__)] = None
                else:
                    shape[self.transform(field.__NAME__)] = None

        if plugins:
            for plugin in plugins:
                shape = plugin(shape)

        imports = [
            f"import {iface} from '../interfaces/{iface}'"
            for iface in interface_names
        ]

        imports.extend(
            f"import {node.__class__().__NAME__} from './{node.__class__().__NAME__}'"
            for node in self.fields if isinstance(node, Node)
        )

        output = JS_TPL.format(
            name=self.__NAME__,
            shape=to_js_shape(shape, indent),
            interfaces=str(interface_names).replace("'", ''),
            imports='\n' + '\n'.join(imports) if imports else ''
        )

        return to_js_keys(output)
