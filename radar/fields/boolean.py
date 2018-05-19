from .field import Field


__all__ = 'Bool',


class Bool(Field):
    __slots__ = Field.__slots__

    def __init__(self, *a, cast=bool, **kw):
        super().__init__(*a, cast=cast, **kw)
