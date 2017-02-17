from maestro.fields.field import Field


class Float(Field):

    def __init__(self, resolver, key=False, not_null=False, default=None,
                 cast=None):
        cast = cast or float
        super().__init__(resolver, key=key, not_null=not_null, default=default,
                         cast=cast)
