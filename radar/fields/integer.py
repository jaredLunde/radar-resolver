from .field import Field


__all__ = 'Int',


class Int(Field):
    __slots__ = Field.__slots__

    def __init__(self, *a, cast=int, **kw):
        super().__init__(*a, cast=cast, **kw)
