from vital.debug import preprX
from maestro.members import Members
from maestro.node import Node
from maestro.exceptions import QueryError, NodeIsNull


class Query(Members):

    def __init__(self, plugins=None, callback=None):
        self.__NAME__ = self.__NAME__ if hasattr(self, '__NAME__') else \
                        self.__class__.__name__
        self.callback = callback
        self.nodes = []
        self.plugins =[]
        self.node_names = []
        self.params = {}
        self.required_nodes = None
        self.install(*plugins or [])
        self._compile()

    __repr__ = preprX('__NAME__', address=False)

    def _compile(self):
        """ Sets :class:Node attributes """
        add_node = self.nodes.append
        add_node_name = self.node_names.append
        set_node = self.__setattr__

        for node_name, node in self._getmembers():
            if isinstance(node, Node):
                node = node.copy()
                add_node(node)
                add_node_name(node_name)
                set_node(node_name, node)

        if not len(self.nodes):
            raise QueryError(f'Query `{self.__NAME__}` does not have any '
                              'assigned Nodes. Queries must include returnable '
                              'Nodes.')

    def install(self, *plugins):
        self.plugins.extend(plugins)

    def execute_plugins(self, **params):
        for plugin in self.plugins:
            plugin(self, **params)

    def get_required_nodes(self, nodes):
        if nodes:
            for node_name, fields in nodes.items():
                try:
                    node = getattr(self, node_name)
                except AttributeErrror:
                    raise QueryError(f'Node `{node_name}` not found in '
                                     f'Query `{self.__NAME__}`.')

                yield (node_name, node.get_required_fields(fields))
        else:
            for node in self.nodes:
                yield (node.__NAME__, node.get_required_fields())

    def require(self, **nodes):
        self.required_nodes = dict(self.get_required_nodes(nodes))
        return self

    def resolve(self, **params):
        out = {}

        self.params = params
        self.required_nodes = self.required_nodes or \
                              dict(self.get_required_nodes({}))

        #: Execute local plugins
        self.execute_plugins(**params)
        #: Executes the apply function which is meant to perform the actual
        #  query task
        self.apply(**params)

        for node_name, fields in self.required_nodes.items():
            node = getattr(self, node_name).copy()

            try:
                result = node.resolve(self, fields)
            except NodeIsNull:
                result = None

            out[node_name] = result

        try:
            return self.callback(self, out)
        except TypeError:
            return out

    def copy(self):
        return self.__class__(plugins=self.plugins, callback=self.callback)
