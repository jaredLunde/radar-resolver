import json
from vital.debug import preprX

from maestro.fields import Field, Obj
from maestro.exceptions import FieldNotFound, NodeKeyError
from maestro.members import Members
from maestro.utils import to_js_keys


JS_TPL = '''const {name} = Maestro.createSchema({
  name: '{name}',
  fields: {shape}
})'''


class Node(Members):

    def __init__(self, callback=None, many=False):
        """ @many: will return #list if @many is |True|
        """
        self.__NAME__ = self.__NAME__ if hasattr(self, '__NAME__') else \
                        self.__class__.__name__
        self.fields = []
        self.parent = None
        self._key = None
        self.callback = callback
        self.many = many
        self._compile()

    __repr__ = preprX('__NAME__', 'fields', address=False)

    def _compile(self):
        """ Sets :class:Field attributes """
        for field_name, field in self._getmembers():
            if isinstance(field, (Field, Node)):
                self.add_field(field_name, field)

        if self._key is None:
            raise NodeKeyError(f'Node `{self.__NAME__}` does not have a '
                                 'designated key but requires one.')

    def add_field(self, field_name, field):
        field = field.copy()
        field.__NAME__ = field_name
        self.fields.append(field)
        setattr(self, field_name, field)

        if isinstance(field, Field) and field.key is True:
            self._key = field

    @property
    def key(self):
        if self._key.value is not None:
            return self._key.value

        raise NodeKeyError(f'Node `{self.__NAME__}` did not have a Key field '
                           'with a value. Your Key field cannot ever return '
                           'None.')

    def to_js(self, indent=2, plugins=None):
        shape = {}

        for field in self.fields:
            if isinstance(field, self.__class__):
                shape[field.__NAME__] = field.to_js()
            else:
                shape[field.__NAME__] = field.default

        if plugins:
            for plugin in plugins:
                shape = plugin(shape)

        output = JS_TPL.format(name=self.__NAME__,
                               shape=json.dumps(shape, indent=indent))

        return to_js_keys(output)

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
                if child_fields or _field.__NAME__ in child_fields
            }
        else:
            fields[field.__NAME__] = None

        return fields

    def get_required_fields(self, input_fields=None):
        fields = {}

        if input_fields is None or not len(input_fields):
            for field in self.fields:
                fields.update(self.get_required_field(field))
        else:
            for field_name, child_fields in input_fields.items():
                field = getattr(self, field_name)
                required_fields = self.get_required_field(field, child_fields)
                fields.update(required_fields)

        return fields

    def resolve_field(self, field_name, sub_fields=None):
        field = self.get_field(field_name)

        if isinstance(field, Node):
            return field.resolve(self, sub_fields)
        else:
            if sub_fields is None:
                return field.resolve(self)

            return field.resolve(self, sub_fields)

    def resolve_fields(self, fields):
        if fields:
            for field_name, sub_fields in fields.items():
                if sub_fields is not None:
                    yield (field_name,
                           self.resolve_field(field_name, sub_fields))
                else:
                    yield (field_name, self.resolve_field(field_name))
        else:
            for field in self.fields:
                yield (field.__NAME__, self.resolve_field(field.__NAME__))

    def _resolve(self, fields):
        out = {name: value for name, value in self.resolve_fields(fields)}

        if self._key.__NAME__ not in fields:
            self.resolve_field(self._key.__NAME__)

        out['@key'] = self.key

        try:
            return self.callback(self, out)
        except TypeError:
            return out

    def _resolve_many(self, fields):
        return [node._resolve(fields) for node in self]

    def resolve(self, parent, fields):
        self.clear()
        self.set_parent(parent)

        if self.many:
            return self._resolve_many(fields)
        else:
            return self._resolve(fields)

    def set_parent(self, parent):
        self.parent = parent
        return self

    def clear(self):
        for field in self.fields:
            field.clear()

        return self

    def copy(self):
        cls = self.__class__(callback=self.callback, many=self.many)
        cls.parent = self.parent
        return cls
