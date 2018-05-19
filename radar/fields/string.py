from .field import Field


__all__ = 'String',


class String(Field):
    __slots__ = Field.__slots__

    def __init__(self, *a, cast=str, **kw):
        super().__init__(*a, cast=cast, **kw)
