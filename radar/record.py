from vital.debug import preprX
from .fields import Field, Obj
from .exceptions import FieldNotFound, RecordKeyError, RecordIsNull
from .interface import Interface
from .utils import to_js_key, to_js_shape


__all__ = 'Record', 'get_interface_fields',


def get_interface_fields(record):
    fields = record.fields
    for interface_cls in record.implements:
        for field in interface_cls().fields:
            if field not in fields:
                setattr(record, field.__NAME__, field)
                yield field


class Record(Interface):
    def __init__(self, many=False, callback=None):
        """ @many: will return #list if @many is |True| """
        super().__init__()
        self._many = many
        self._callback = callback

    __repr__ = preprX('__NAME__', 'fields', address=False)

    def __new__(cls, *a, **kw):
        record = super().__new__(cls)
        record.__init__(*a, **kw)

        if hasattr(record, 'implements'):
            fields = get_interface_fields(record)
            record.fields = tuple((*fields, *record.fields))

        for field in record.fields:
            if isinstance(field, Field) and field.key is True:
                record._key = field
                return record

        raise RecordKeyError(f'Record `{cls.__name__}` does not have a Key field.')

    def get_field(self, field_name):
        field = getattr(self, field_name)

        if isinstance(field, (Field, Record)):
            return field

        raise FieldNotFound(f'Field named `{field_name}` was not found in '
                            f'Record `{self.__NAME__}`')

    def get_required_field(self, field, child_fields=None):
        if isinstance(field, Record):
            yield field.__NAME__, field.get_required_fields(child_fields)
        elif isinstance(field, Obj):
            yield (
                field.__NAME__,
                {
                    child_field.__NAME__: dict(self.get_required_field(
                        child_field,
                        child_fields[child_field.__NAME__] if child_fields else None
                    ))
                    for child_field in field.fields
                    if child_fields and child_field.__NAME__ in child_fields
                }
            )
        else:
            yield field.__NAME__, None

    def get_required_fields(self, input_fields=None):
        #: TODO: tailcall optimiztaion w/ while loop
        output = {}

        if input_fields is None or not len(input_fields):
            for field in self.fields:
                for k, v in self.get_required_field(field):
                    output[k] = v
        else:
            for field_name, child_fields in input_fields.items():
                # field_name = to_python_key(field_name)
                field = self.get_field(field_name)
                for k, v in self.get_required_field(field, child_fields):
                    output[k] = v

        return output

    def resolve_field(self, field_name, state, fields=None, record=None, **context):
        field = self.get_field(field_name)

        if isinstance(field, Record):
            try:
                return field.resolve(fields, state, record=self, **context)
            except RecordIsNull:
                return None
        else:
            if fields is None:
                return field.resolve(state, record=self, **context)

            return field.resolve(state, record=self, fields=fields, **context)

    def resolve_fields(self, fields, state, **context):
        if fields:
            fields = fields.items() if hasattr(fields, 'items') else fields
            for field_name, nested in fields:
                if nested is not None:
                    yield (
                        field_name,
                        self.resolve_field(field_name, state, fields=nested, **context)
                    )
                else:
                    yield (
                        field_name,
                        self.resolve_field(field_name, state, **context)
                    )
        else:
            for field in self.fields:
                yield (
                    field.__NAME__,
                    self.resolve_field(field.__NAME__, state, **context)
                )

    def _resolve(self, fields, state, index=None, **context):
        state = self.reduce(state, fields=fields, index=index, **context) or {}

        if not isinstance(state, dict):
            raise TypeError('Data returned by `reduce` methods must be of type'
                            f'`dict`. "{state}" is not a dict in Record: '
                            f'{self.__class__.__name__}')

        output = {
            to_js_key(name): value
            for name, value in self.resolve_fields(fields, state, **context)
        }

        key_name = to_js_key(self._key.__NAME__)

        if key_name not in fields:
            output[key_name] = self.resolve_field(
                self._key.__NAME__,
                state,
                fields=fields,
                **context
            )

        if output[key_name] is None:
            raise RecordKeyError(
                f'Record `{self.__NAME__}` did not have a Key field '
                'with a value. Your Key field cannot ever return None.'
            )

        try:
            return self._callback(self, output)
        except TypeError:
            return output

    def _resolve_many(self, *a, index=None, **kw):
        ''' includes index outside of kwargs in order to ignore it '''
        index = 0
        output = []
        add_output = output.append

        while True:
            try:
                add_output(self._resolve(*a, index=index, **kw))
            except IndexError:
                break

            index += 1

        return output

    def resolve(self, fields, state,  **context):
        if self._many:
            resolver = self._resolve_many
        else:
            resolver = self._resolve

        return resolver(fields, state, **context)

    def clear(self):
        for field in self.fields:
            field.clear()

        return self

    def reduce(self, state, index=None, **context):
        if context.get('record'):
            state = state[self.__NAME__]
        if state is None:
            raise RecordIsNull()
        if index is None:
            return state
        else:
            return state[index]

    def copy(self):
        cls = self.__class__(callback=self._callback, many=self._many)
        return cls


'''
from radar import Interface, Record, fields

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

MyRecord()
Timer(MyRecord).time(1E4)
MyRecord.fields
MyRecord().resolve({'foo': None}, {'foo': 'bar', 'bar': 'baz'})
Timer(MyRecord().resolve, fields={'foo': None}, state={'foo': 'bar', 'bar': 'baz'}).time(1E4)

class MyNestedRecord(Record):
    implements = [MySubInterface]
    boz = fields.Float()


class MyRecord(Record):
    uid = fields.String(key=True)
    nested = MyNestedRecord(many=True)

MyRecord().resolve({'nested': {'foo': None}, 'uid': None}, {'nested': [{'foo': 'bar', 'bar': 'baz'}], 'uid': 1})
'''
