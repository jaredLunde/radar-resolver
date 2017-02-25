from radar.fields.field import Field


class Int(Field):

    def __init__(self, resolver, key=False, not_null=False, default=None,
                 cast=None):
        cast = cast or int
        super().__init__(resolver, key=key, not_null=not_null, default=default,
                         cast=cast)
