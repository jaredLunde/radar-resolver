from vital.debug import preprX


__all__ = ('Field',)


def _cast(x):
    return x


class Field(object):

    def __init__(self, resolver=None, key=False, not_null=False, default=None,
                 cast=None):
        """ @key: Universally unique field which identifies your Schema """
        self.resolver = resolver
        self.not_null = not_null
        self.cast = cast or _cast
        self.default = default
        self.key = key
        self.value = None
        self.__NAME__ = None

    __repr__ = preprX('name', 'value', 'key', address=False)

    def set_value(self, value=None):
        if value is not None:
            self.value = self.cast(value)
        elif value is None and self.default is None and self.not_null:
            raise ValueError(f'Field `{self.__NAME__}` cannot be null.')
        elif value is None and self.default is not None:
            self.value = self.default
        else:
            self.value = None

        return self.value

    def default_resolver(self, query=None, node=None, **data):
        try:
            return data[self.__NAME__]
        except KeyError:
            raise KeyError(f'Key `{field_name}` not found in Node'
                           f'`{self.__NAME__}` containing `{data}`')

    def clear(self):
        self.value = None
        return self

    def copy(self):
        return self.__class__(self.resolver,
                              key=self.key,
                              not_null=self.not_null,
                              default=self.default,
                              cast=self.cast)

    def resolve(self, query=None, node=None, **data):
        resolver = self.resolver or self.default_resolver
        return self.set_value(resolver(query=query, node=node, **data))
