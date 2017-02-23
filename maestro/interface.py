from maestro.node import Node
from maestro.fields.field import Field


class Interface(Node):
    key = None

    def __init__(self, *args, **kwargs):
        self.implementation_fields = []
        super().__init__(*args, **kwargs)
        del self._key

    def _compile(self):
        for field_name, field in self._getmembers():
            if isinstance(field, (Node, Field)):
                self.add_field(field_name, field)

        for field in self.fields:
            for ifield in self.implementation_fields:
                field.add_field(ifield.__NAME__, ifield)

    def add_field(self, field_name, field):
        is_field = isinstance(field, Field)
        is_node = isinstance(field, Node)

        if is_field:
            field = field.copy()
            field.__NAME__ = field_name
            self.implementation_fields.append(field)

        if is_node:
            field.__NAME__ = field_name
            self.fields.append(field)

        setattr(self, field_name, field)

    @property
    def resolve_type(self):
        raise TypeError('Interfaces require a `resolve_type` property which '
                        'returns a string specifying the proper Node to '
                        'resolve for each iteration.')

    def resolve_fields(self, fields={}):
        field_name = self.resolve_type
        result = self.resolve_field(field_name, fields.get(field_name))
        result['@node'] = field_name

        return result

    def _resolve(self, fields):
        out = self.resolve_fields(fields)

        try:
            return self.callback(self, out)
        except TypeError:
            return out
