from vital.debug import preprX


__all__ = 'Field',


def default_cast(x):
    return x


def default_resolver(field_name, state, record=None, query=None, **context):
    try:
        return state[field_name]
    except (KeyError, TypeError):
        raise KeyError(
            f'Key `{field_name}` not found in Record  `{record.__NAME__}` of '
            f'Query `{query.__NAME__}`.'
        )


class Field(object):
    __slots__ = 'key', 'cast', 'resolver', 'not_null', 'default', '__NAME__'

    def __init__(
        self,
        resolver=default_resolver,
        key=False,
        not_null=False,
        default=None,
        cast=default_cast
    ):
        """ @key: Universally unique field which identifies your Schema """
        self.resolver = resolver
        self.not_null = not_null
        self.cast = cast
        self.default = default
        self.key = key
        self.__NAME__ = None

    __repr__ = preprX('__NAME__', 'key', address=False)

    def __call__(self, value=None):
        if value is not None:
            try:
                return self.cast(value) if not isinstance(value, self.cast) else value
            except TypeError:
                return self.cast(value)
        else:
            if self.default is None:
                if self.not_null:
                    raise ValueError(f'Field `{self.__NAME__}` cannot be null.')
                else:
                    return None
            else:
                return self.default

    def copy(self):
        return self.__class__(
            self.resolver,
            key=self.key,
            not_null=self.not_null,
            default=self.default,
            cast=self.cast
        )

    def resolve(self, state, **context):
        output = self.resolver(self.__NAME__, state, **context)
        return self.__call__(output)
