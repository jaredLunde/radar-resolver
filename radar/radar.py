try:
    import ujson as json
except ImportError:
    import json

from radar.exceptions import QueryError, ActionError, OperationNotFound


class Radar(object):

    def __init__(self, queries=None, actions=None, raises=True,
                 transform_keys=True):
        """ @transform_keys: if |True|, transforms JS camelCase keys to Python
                underscore_case and vice-versa
        """
        self.queries = {}
        self.install_query(*queries or [])
        self.actions = {}
        self.install_action(*actions or [])
        self.raises = raises
        self.transform_keys = transform_keys

    def __call__(self, data, is_json=True):
        return self.resolve(data, is_json=is_json)

    def install_query(self, *queries):
        self.queries.update({
            query.__NAME__
                if hasattr(query, '__NAME__') else query.__name__: query
            for query in queries
        })

    def install_action(self, *actions):
        self.actions.update({
            action.__NAME__ if hasattr(action, '__NAME__') else action.__name__:
                action
            for action in actions or []
        })

    def remove_query(self, *queries):
        for query in queries:
            del self.queries[query.name]

    def remove_actions(self, *actions):
        for action in actions:
            del self.actions[action.name]

    def get_query(self, query_name):
        return self.queries[query_name].copy()

    def get_action(self, action_name):
        return self.actions[action_name].copy()

    def resolve_query(self, query_data):
        query_requires = query_data.get('requires')
        query_params = query_data.get('params', {})
        query = self.get_query(query_data['type'])
        result = None

        try:
            if query_requires:
                query.require(**query_requires)

            query.transform_keys(self.transform_keys)

            result = query.resolve(**query_params)
        except QueryError as e:
            result[query.__NAME__] = str(e)
        except Exception as e:
            if self.raises:
                raise e

            result = {'error': 'An uncaught error occurred.'}

        return result

    def resolve_action(self, action_data):
        action_input = action_data.get('input', {})
        action_requires = action_data.get('requires', {})
        action = self.get_action(action_data['type'])

        if action_requires:
            action.require(**action_requires)

        action.transform_keys(self.transform_keys)

        return action.resolve(**action_input)

    def resolve(self, operations, is_json=True):
        operations = json.loads(operations) if is_json else operations

        out = []
        add_out = out.append

        for operation in operations:
            if operation['type'] in self.queries:
                add_out(self.resolve_query(operation))
            elif operation['type'] in self.actions:
                add_out(self.resolve_action(operation))
            else:
                raise OperationNotFound('An action or query with the name '
                                        f'{operation.type} was not found.')

        return out