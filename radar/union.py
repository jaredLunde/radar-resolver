from radar.record import Record
from radar.fields.field import Field


class Union(Record):
    key = None

    def __init__(self, *args, **kwargs):
        self.implementation_fields = []
        super().__init__(*args, **kwargs)
        del self._key

    def _compile(self):
        for record_name, record in self._getmembers():
            if isinstance(record, Record):
                self.add_record(record_name, record)

    def add_record(self, record_name, record):
        record.__NAME__ = record_name
        self._fields.append(record)

        setattr(self, record_name, record)

    @property
    def records(self):
        return self._fields

    def get_record_type(self, *args, **kwargs):
        raise TypeError('Unions require a `get_record_type` method which '
                        'returns a string specifying the proper Record to '
                        'resolve for each resolution.')

    def get_field(self, field_name):
        field = getattr(self, field_name)

        if isinstance(field, Record):
            return field

        raise FieldNotFound(f'Field named `{field_name}` was not found in '
                            f'Record `{self.__NAME__}`')

    def resolve_fields(self, query, fields, record=None, **data):
        fields = fields or {}
        record_type = self.get_record_type(query=query, fields=fields, **data)

        if record_type is None:
            raise TypeError('Unions must return a string from their '
                            '`get_record_type` method specifying the proper Record'
                            'to resolve for each resolution. Check the '
                            f'`get_record_type` method of {self.__class__.__name__}')


        result = {
            self.transform(record_type): self.resolve_field(
                query,
                record_type,
                fields.get(record_type),
                **data
            )
        }
        # result['@union'] = self.transform(record_type)

        return result

    def _resolve(self, query, fields, index=None, **data):
        data = self.apply(query, fields, index=index, **data) or {}

        if not isinstance(data, dict):
            raise TypeError('Data returned by `apply` methods must be of type'
                            f'`dict`. "{data}" is not a dict in Record: '
                            f'{self.__class__.__name__}')

        out = self.resolve_fields(query, fields, index=index, **data)

        try:
            return self.callback(self, out)
        except TypeError:
            return out
