from vital.debug import preprX
from .record import Record
from .interface import Interface
from .exceptions import (
    QueryError,
    QueryErrors,
    ActionErrors,
    RecordIsNull,
    MissingApplyMethod
)
from .utils import to_python_key, get_class_attrs


__all__ = 'transform_deep_keys', 'Query'


def transform_deep_keys(props):
    return {
        to_python_key(key): (
            val if not isinstance(val, dict) else transform_deep_keys(val)
        )
        for key, val in props.items()
    }


def get_records(attrs):
    for k, v in attrs.items():
        record = attrs[k]

        if isinstance(record, Record):
            record.__NAME__ = k
            yield record


class MetaQuery(type):
    def __new__(cls, name, bases, attrs):
        attrs['records'] = tuple(get_records(attrs))
        return super().__new__(cls, name, bases, attrs)


class Query(object, metaclass=MetaQuery):
    __slots__ = 'callback',

    def __init__(self, callback=None):
        self._callback = callback

    __repr__ = preprX('records', address=False)

    def __new__(cls, *a, **kw):
        query = super().__new__(cls)
        query.__init__(*a, **kw)
        query.records = tuple(
            record
            for k, record in get_class_attrs(query.__class__)
            if isinstance(record, (Record, Interface))
        )

        if not len(query.records):
            raise QueryError(
                f'Query `{cls.__name__}` does not have any assigned Records. '
                'Queries must include returnable Records.'
            )

        try:
            setattr(query, '__call__', query.apply)
        except AtrributeError:
            raise MissingApplyMethod(
                f'Query {name} is missing an `apply` method. All queries must '
                'include an `apply` method which returns state for the records.'
            )

        return query

    def get_required_records(self, records):
        if records:
            try:
                for record_name, fields in records.items():
                    yield (
                        record_name,
                        getattr(self, record_name).get_required_fields(fields)
                    )
            except AttributeError:
                raise QueryError(
                    f'Record `{record_name}` not found in '
                    f'Query `{self.__class__.__name__}`.'
                )
        else:
            for record in self.records:
                yield (
                    record.__NAME__,
                    getattr(self, record.__NAME__).get_required_fields()
                )

    def resolve(self, records, props):
        required_records = dict(
            self.get_required_records(transform_deep_keys(records) or {})
        )

        # executes the apply function which is meant to fetch the result of
        # the actual query task
        state = self.apply(required_records, **transform_deep_keys(props))
        state = {} if state is None else state
        output = {}

        for record_name, fields in required_records.items():
            try:
                result = getattr(self, record_name).resolve(
                    fields,
                    state,
                    query=self
                )
            except RecordIsNull:
                result = None

            output[record_name] = result

        if self._callback:
            return self._callback(output, query=self)
        else:
            return output

    def copy(self):
        return self.__class__(callback=self._callback)


'''
from radar import Interface, Record, Query, fields
from vital.debug import Timer

class MyInterface(Interface):
    foo = fields.String(key=True)
    bar = fields.Int()

class MySubInterface(MyInterface):
    baz = fields.Array()

MySubInterface()

Timer(MySubInterface).time(1E4)

class MyRecord(Record):
    implements = [MySubInterface]
    boz = fields.Float()

MyRecord()
Timer(MyRecord).time(1E4)
MyRecord.fields
MyRecord().resolve({'foo': None}, {'foo': 'bar', 'bar': 'baz'})
Timer(MyRecord().resolve, fields={'foo': None}, state={'foo': 'bar', 'bar': 'baz'}).time(1E4)

class MyQuery(Query):
    my = MyRecord()
    def apply(*args, **kwargs):
        return {'foo': 'bar', 'bar': 1, 'baz': ['a', 'b'], 'boz': 1.0}


class MyQueries(Query):
    my = MyRecord(many=True)
    def apply(*args, **kwargs):
        return [{'foo': 'bar', 'bar': 1, 'baz': ['a', 'b'], 'boz': 1.0}, {'foo': 'bar', 'bar': 2, 'baz': ['c', 'd'], 'boz': 2.0}]


MyQuery().resolve({'my': {'foo': None}}, {})
MyQueries().resolve({'my': {'foo': None}}, {})
Timer(MyQueries().resolve, records={'my': {'foo': None}}, props={}).time(1E4)
Timer(MyQuery().resolve, records={'my': {}}, props={}).time(1E4)
'''
