from .field import Field
from ..interface import Interface
from ..exceptions import FieldNotFound
from ..utils import to_js_key


__all__ = 'Obj',


class Obj(Field, Interface):
    __slots__ = Field.__slots__

    def __init__(self, not_null=False, default=None, cast=dict):
        def resolver(state, fields=None, **context):
            return {
                to_js_key(field.__NAME__): field.resolve(state[self.__NAME__], **context)
                for field in self.get_fields(fields)
            }

        super().__init__(
            resolver,
            key=False,
            not_null=not_null,
            default=default,
            cast=cast
        )

    def get_fields(self, fields):
        if fields is None:
            for field in self.fields:
                yield field
        else:
            for field_name in fields:
                field = getattr(self, field_name)
                if field in self.fields:
                    yield field
                else:
                    raise FieldNotFound(f'Field "{field}" was not found in '
                                        f'the object "{self.__NAME__}"')

    def resolve(self, state, **context):
        return self.__call__(self.resolver(state, **context))

    def copy(self):
        return self.__class__(not_null=self.not_null,
                              default=self.default,
                              cast=self.cast)

'''
from radar import Record, fields
from vital.debug import Timer

class MyObj(fields.Obj):
    foo = fields.String()


class MyRecord(Record):
    uid = fields.Int(key=True)
    my = MyObj()

my = MyObj()
my.__NAME__ = 'my'
my.resolve({'my': {'foo': 'bar', 'bar': 'baz'}})
MyRecord().resolve({'my': None}, {'my': {'foo': 'bar', 'bar': 'baz'}, 'uid': 1234})

Timer(my.resolve, state={'my': {'foo': 'bar', 'bar': 'baz'}}).time(1E4)
'''
