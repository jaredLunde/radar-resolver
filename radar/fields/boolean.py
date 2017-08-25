from radar.fields.field import Field


class Bool(Field):

    def __init__(self, resolver=None, not_null=False, default=None, cast=None):
        cast = cast or bool
        super().__init__(resolver, key=False, not_null=not_null,
                         default=default, cast=cast)

    def copy(self):
        return self.__class__(self.resolver,
                              not_null=self.not_null,
                              default=self.default,
                              cast=self.cast)
