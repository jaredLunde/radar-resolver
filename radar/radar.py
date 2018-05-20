try:
    import ujson as json
except ImportError:
    import json

from radar.exceptions import (
    QueryError,
    ActionError,
    ActionError,
    QueryErrors,
    OperationNotFound
)


empty_dict = {}

class Radar(object):
    __slots__ = 'queries', 'actions', 'raises'
    
    def __init__(self, queries=None, actions=None, raises=True):
        self.queries = {}
        self.actions = {}
        if queries:
            self.install_query(*queries)
        if actions:
            self.install_action(*actions)
        self.raises = raises

    def __call__(self, state, is_json=True):
        return self.resolve(state, is_json=is_json)

    def install_query(self, *queries):
        for query in queries:
            query_name = (
                query.__NAME__
                if hasattr(query, '__NAME__') else
                query.__class__.__name__
            )
            query.__NAME__ = query_name
            self.queries[query_name] = query

    def install_action(self, *actions):
        for action in actions:
            action_name = (
                action.__NAME__
                if hasattr(action, '__NAME__') else
                action.__class__.__name__
            )
            action.__NAME__ = action_name
            self.actions[action_name] = action


    def remove_query(self, *queries):
        for query in queries:
            del self.queries[query.name]

    def remove_actions(self, *actions):
        for action in actions:
            del self.actions[action.name]

    def get_query(self, query_name):
        return self.queries[query_name]

    def get_action(self, action_name):
        return self.actions[action_name]

    def resolve_query(self, query_data):
        query_requires = query_data.get('contains', empty_dict)
        query_params = query_data.get('props', empty_dict)
        query = self.get_query(query_data['name'])
        result = {}

        try:
            result = query.resolve(query_requires, query_params)
        except (QueryError, ActionError, ActionError, QueryErrors):
            result = None
        except Exception as e:
            if self.raises:
                raise e

        return result

    def resolve_action(self, action_data):
        action_input = action_data.get('props', empty_dict)
        action_requires = action_data.get('contains', empty_dict)
        action = self.get_action(action_data['name'])
        result = {}

        try:
            result = action.resolve(action_requires, action_input)
        except (QueryError, ActionError, ActionError, QueryErrors):
            result = None
        except Exception as e:
            if self.raises:
                raise e

        return result

    def resolve(self, operations, is_json=True):
        operations = json.loads(operations) if is_json else operations

        out = []
        add_out = out.append

        for operation in operations:
            if operation is None:
                add_out(None)
            elif operation['name'] in self.queries:
                add_out(self.resolve_query(operation))
            elif operation['name'] in self.actions:
                add_out(self.resolve_action(operation))
            else:
                raise OperationNotFound('An action or query with the name '
                                        f'{operation.type} was not found.')

        return out
