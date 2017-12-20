from vital.debug import preprX
from radar.members import Members
from radar.node import Node
from radar.interface import Interface
from radar.exceptions import QueryError, QueryErrors, ActionErrors, NodeIsNull
from radar.utils import transform_keys


def transform_deep_keys(props, do_transform=True):
    return {transform_keys(key, do_transform, False):
            (val if not isinstance(val, dict) else
             transform_deep_keys(val, do_transform))
            for key, val in props.items()}


class Query(Members):

    def __init__(self, plugins=None, callback=None):
        self.__NAME__ = self.__NAME__ if hasattr(self, '__NAME__') else \
                        self.__class__.__name__
        self.callback = callback
        self.nodes = []
        self.plugins = []
        self.node_names = []
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

    def execute_plugins(self, **props):
        for plugin in self.plugins:
            plugin(self, **props)

    def get_required_nodes(self, nodes):
        rn = {}

        if nodes:
            for node_name, fields in nodes.items():
                node_name = self.transform(node_name, False)

                try:
                    node = getattr(self, node_name).copy()
                    node.transform_keys(self._transform_keys)
                except AttributeError:
                    raise QueryError(f'Node `{node_name}` not found in '
                                     f'Query `{self.__NAME__}`.')

                rn[node_name] = node.get_required_fields(fields)
        else:
            for node_name in self.node_names:
                node_name = self.transform(node_name, False)
                node = getattr(self, node_name).copy()
                node.transform_keys(self._transform_keys)
                rn[node_name] = node.get_required_fields()

        return rn

    def resolve(self, nodes=None, **props):
        out = {}
        props = transform_deep_keys(props, self._transform_keys)
        required_nodes = self.get_required_nodes(nodes or {})

        #: Execute local plugins
        self.execute_plugins(nodes=required_nodes.copy(), **props)
        #: Executes the apply function which is meant to perform the actual
        #  query task
        data = None

        if hasattr(self, 'apply'):
            data = self.apply(nodes=required_nodes.copy(), **props)
            '''try:
                data = self.apply(nodes=required_nodes.copy(), **props)
            except (QueryErrors, ActionErrors) as e:
                return None
                return e.for_json()'''

        data = {} if data is None else data

        for node_name, fields in required_nodes.items():
            node = getattr(self, node_name).copy()
            node.transform_keys(self._transform_keys)
            node_name = self.transform(node_name)

            try:
                result = node.resolve(self, fields=fields, **data)
            except NodeIsNull:
                result = None
            #except (QueryErrors, ActionErrors) as e:
            #    return None
                # return e.for_json()

            out[node_name] = result

        try:
            return self.callback(self, out)
        except TypeError:
            return out

    def copy(self):
        cls = self.__class__(plugins=self.plugins, callback=self.callback)
        cls._transform_keys = self._transform_keys

        return cls
