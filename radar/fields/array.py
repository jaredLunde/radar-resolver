import functools
from .field import Field


__all__ = 'Array',


def cast_array(cast):
    @functools.wraps(cast)
    def apply(value):
        return list(map(cast, value))
    return apply


class Array(Field):
    __slots__ = Field.__slots__

    def __init__(self, *a, cast=str, **kw):
        super().__init__(*a, cast=cast_array(cast), **kw)
