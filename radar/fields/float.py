from .field import Field


__all__ = 'Float',


class Float(Field):
    __slots__ = Field.__slots__

    def __init__(self, *a, cast=float, **kw):
        super().__init__(*a, cast=cast, **kw)
