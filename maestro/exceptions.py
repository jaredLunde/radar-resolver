class FieldNotFound(Exception):
    pass


class NodeKeyError(Exception):
    pass


class QueryError(Exception):
    pass


class ActionError(Exception):
    pass


class QueryErrors(Exception):

    def __init__(self, *messages, code=None):
        self.messages = list(messages)
        self.code = code

    def for_json(self):
        return [{'message': message, 'code': self.code}
                for message in self.messages]


class ActionErrors(QueryErrors):
    pass


class NodeIsNull(Exception):
    pass


class OperationNotFound(Exception):
    pass
