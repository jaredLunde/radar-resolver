from vital.debug import preprX
from radar.members import Members
from radar.node import Node
from radar.interface import Interface
from radar.exceptions import QueryError, QueryErrors, ActionErrors, NodeIsNull
from radar.utils import transform_keys

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
        self._transform_keys = None
        self._compile()

    __repr__ = preprX('__NAME__', address=False)

    def transform_keys(self, truthy_falsy=None):
        self._transform_keys = True if truthy_falsy is None else truthy_falsy

    def transform(self, field_name, to_js=True):
        return transform_keys(field_name, self._transform_keys, to_js)

    def _compile(self):
        """ Sets :class:Node attributes """
        add_node = self.nodes.append
        add_node_name = self.node_names.append
        set_node = self.__setattr__

        for node_name, node in self._getmembers():
            if isinstance(node, (Node, Interface)):
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
                node_name = self.transform(node_name, False)

                try:
                    node = getattr(self, node_name)
                    node.transform_keys(self._transform_keys)
                    node.set_parent(self)
                except AttributeError:
                    raise QueryError(f'Node `{node_name}` not found in '
                                     f'Query `{self.__NAME__}`.')

                yield (node_name, node.get_required_fields(fields))
        else:
            for node_name in self.node_names:
                node = getattr(self, node_name)
                node.transform_keys(self._transform_keys)
                yield (node_name, node.get_required_fields())

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
        if hasattr(self, 'apply'):
            try:
                self.apply(**params)
            except (QueryErrors, ActionErrors) as e:
                return e.for_json()

        for node_name, fields in self.required_nodes.items():
            node_name = self.transform(node_name)
            node = getattr(self, node_name).copy()
            node.transform_keys(self._transform_keys)
            
            try:
                result = node.resolve(self, fields)
            except NodeIsNull:
                result = None
            except (QueryErrors, ActionErrors) as e:
                return e.for_json()

            out[node_name] = result

        try:
            return self.callback(self, out)
        except TypeError:
            return out

    def copy(self):
        return self.__class__(plugins=self.plugins, callback=self.callback)
