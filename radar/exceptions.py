class FieldNotFound(Exception):
    pass


class MissingApplyMethod(Exception):
    pass


class RecordKeyError(Exception):
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
        return {
            'errors': [{'message': message, 'code': self.code}
                       for message in self.messages]
        }


class ActionErrors(QueryErrors):
    pass


class RecordIsNull(Exception):
    pass


class OperationNotFound(Exception):
    pass
