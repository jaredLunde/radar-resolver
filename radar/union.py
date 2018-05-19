from .interface import Interface
from .record import Record
from .fields import Field
from .query import get_records
from .utils import get_class_attrs, to_js_key


class Union(Record):
    __slots__ = Record.__slots__

    def __new__(cls, *a, **kw):
        union = super(Interface, cls).__new__(cls)
        union.__init__(*a, **kw)
        union.fields = tuple(
            record
            for k, record in get_class_attrs(union.__class__)
            if isinstance(record, (Record, Interface))
        )

        if not len(union.fields):
            raise TypeError(
                f'Union `{cls.__name__}` does not have any assigned Records. '
                'Unions must include returnable Records.'
            )

        if not hasattr(union, 'get_record_type'):
            raise TypeError(
                'Union `{cls.__name__}` does not have a `get_record_type` method.'
                'Unions require a `get_record_type` method which '
                'returns a string specifying the proper Record to '
                'resolve for each resolution.'
            )

        return union

    @property
    def records(self):
        return self.fields

    def get_field(self, field_name):
        field = getattr(self, field_name)

        if isinstance(field, Record):
            return field

        raise FieldNotFound(f'Field named `{field_name}` was not found in '
                            f'Record `{self.__NAME__}`')

    def resolve_fields(self, fields, state, **context):
        fields = fields or {}
        record_type = self.get_record_type(state, fields=fields, **context)

        if record_type is None:
            raise TypeError('Unions must return a string from their '
                            '`get_record_type` method specifying the proper Record'
                            'to resolve for each resolution. Check the '
                            f'`get_record_type` method of {self.__class__.__name__}')

        yield to_js_key(record_type), self.resolve_field(
            record_type,
            state,
            fields=fields.get(record_type),
            **context
        )

    def _resolve(self, fields, state, **context):
        state = self.reduce(state, fields=fields, **context) or {}

        if not isinstance(state, dict):
            raise TypeError('Data returned by `apply` methods must be of type'
                            f'`dict`. "{state}" is not a dict in Record: '
                            f'{self.__class__.__name__}')

        output = dict(self.resolve_fields(fields, state, **context))

        try:
            return self._callback(output, self)
        except TypeError:
            return output

'''
from radar import Interface, Record, Query, Union, fields
from vital.debug import Timer

class MyInterface(Interface):
    foo = fields.String(key=True)
    bar = fields.Int()

class MySubInterface(MyInterface):
    baz = fields.Array()

MySubInterface()

from vital.debug import Timer
Timer(MySubInterface).time(1E4)

class MyRecord(Record):
    implements = [MySubInterface]
    boz = fields.Float()

class MyUnion(Union):
    my = MyRecord()
    def get_record_type(*a, **kw):
        return 'my'

MyUnion().resolve({'my': {'foo': None}}, {'foo': 'bar'})

class MyQuery(Query):
    my = MyUnion()
    def apply(*args, **kwargs):
        return {'foo': 'bar', 'bar': 1, 'baz': ['a', 'b'], 'boz': 1.0}

Timer(MyQuery().resolve, records={'my': {'my': {}}}).time(1E4)
'''
