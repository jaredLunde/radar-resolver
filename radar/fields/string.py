from radar.fields.field import Field


class String(Field):

    def __init__(self, resolver=None, key=False, not_null=False, default=None,
                 cast=None):
        cast = cast or str
        super().__init__(resolver, key=key, not_null=not_null, default=default,
                         cast=cast)
