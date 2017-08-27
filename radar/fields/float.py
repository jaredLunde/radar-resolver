from radar.fields.field import Field


class Float(Field):
    __slots__ = Field.__slots__
    
    def __init__(self, resolver=None, key=False, not_null=False, default=None,
                 cast=None):
        cast = cast or float
        super().__init__(resolver, key=key, not_null=not_null, default=default,
                         cast=cast)
