from radar.fields.field import Field


class Array(Field):
    __slots__ = Field.__slots__

    def __init__(self, resolver=None, not_null=False, default=None, cast=None):
        cast = cast or str
        super().__init__(resolver, not_null=not_null, default=default,
                         cast=cast, key=False)

    def get_value(self, value=None):
        if value is not None:
            return list(map(self.cast, value))
        elif value is None and self.default is None and self.not_null:
            raise ValueError(f'Field `{self.name}` cannot be null.')
        elif value is None and self.default is not None:
            return self.default

    def copy(self):
        return self.__class__(self.resolver,
                              not_null=self.not_null,
                              default=self.default,
                              cast=self.cast)
