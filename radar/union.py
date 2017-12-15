from radar.node import Node
from radar.fields.field import Field


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

    def get_node_type(self, *args, **kwargs):
        raise TypeError('Unions require a `get_node_type` method which '
                        'returns a string specifying the proper Node to '
                        'resolve for each resolution.')

    def get_field(self, field_name):
        field = getattr(self, field_name)

        if isinstance(field, Node):
            return field

        raise FieldNotFound(f'Field named `{field_name}` was not found in '
                            f'Node `{self.__NAME__}`')

    def resolve_fields(self, query, fields, node=None, **data):
        fields = fields or {}
        node_type = self.get_node_type(query=query, fields=fields, **data)

        if node_type is None:
            raise TypeError('Unions must return a string from their '
                            '`get_node_type` method specifying the proper Node'
                            'to resolve for each resolution. Check the '
                            f'`get_node_type` method of {self.__class__.__name__}')


        result = {
            self.transform(node_type): self.resolve_field(
                query,
                node_type,
                fields.get(node_type),
                **data
            )
        }
        # result['@union'] = self.transform(node_type)

        return result

    def _resolve(self, query, fields, index=None, **data):
        data = self.apply(query, fields, index=index, **data) or {}

        if not isinstance(data, dict):
            raise TypeError('Data returned by `apply` methods must be of type'
                            f'`dict`. "{data}" is not a dict in Node: '
                            f'{self.__class__.__name__}')

        out = self.resolve_fields(query, fields, index=index, **data)

        try:
            return self.callback(self, out)
        except TypeError:
            return out
