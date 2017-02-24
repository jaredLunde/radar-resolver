from maestro.node import Node
from maestro.fields.field import Field


class Union(Node):
    key = None

    def __init__(self, *args, **kwargs):
        self.implementation_fields = []
        super().__init__(*args, **kwargs)
        del self._key

    def _compile(self):
        for node_name, node in self._getmembers():
            if isinstance(node, Node):
                self.add_node(node_name, node)

    def add_node(self, node_name, node):
        node.__NAME__ = node_name
        self._fields.append(node)

        setattr(self, node_name, node)

    @property
    def nodes(self):
        return self._fields

    @property
    def node_type(self):
        raise TypeError('Unions require a `node_type` property which '
                        'returns a string specifying the proper Node to '
                        'resolve for each iteration.')

    def resolve_fields(self, fields={}):
        node_type = self.node_type
        result = self.resolve_field(node_type, fields.get(node_type))
        result['@union'] = node_type

        return result

    def _resolve(self, fields):
        out = self.resolve_fields(fields)

        try:
            return self.callback(self, out)
        except TypeError:
            return out
