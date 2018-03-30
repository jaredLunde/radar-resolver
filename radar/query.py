from vital.debug import preprX
from radar.members import Members
from radar.record import Record
from radar.interface import Interface
from radar.exceptions import QueryError, QueryErrors, ActionErrors, RecordIsNull
from radar.utils import transform_keys


def transform_deep_keys(props, do_transform=True):
    return {transform_keys(key, do_transform, False):
            (val if not isinstance(val, dict) else
             transform_deep_keys(val, do_transform))
            for key, val in props.items()}


class Query(Members):

    def __init__(self, plugins=None, callback=None):
        self.__NAME__ = self.__NAME__ if hasattr(self, '__NAME__') else \
                        self.__class__.__name__
        self.callback = callback
        self.records = []
        self.plugins = []
        self.record_names = []
        self.install(*plugins or [])
        self._transform_keys = None
        self._compile()

    __repr__ = preprX('__NAME__', address=False)

    def transform_keys(self, truthy_falsy=None):
        self._transform_keys = True if truthy_falsy is None else truthy_falsy

    def transform(self, field_name, to_js=True):
        return transform_keys(field_name, self._transform_keys, to_js)

    def _compile(self):
        """ Sets :class:Record attributes """
        add_record = self.records.append
        add_record_name = self.record_names.append
        set_record = self.__setattr__

        for record_name, record in self._getmembers():
            if isinstance(record, (Record, Interface)):
                record = record.copy()
                add_record(record)
                add_record_name(record_name)
                set_record(record_name, record)

        if not len(self.records):
            raise QueryError(f'Query `{self.__NAME__}` does not have any '
                              'assigned Records. Queries must include returnable '
                              'Records.')

    def install(self, *plugins):
        self.plugins.extend(plugins)

    def execute_plugins(self, **props):
        for plugin in self.plugins:
            plugin(self, **props)

    def get_required_records(self, records):
        rn = {}

        if records:
            for record_name, fields in records.items():
                record_name = self.transform(record_name, False)

                try:
                    record = getattr(self, record_name).copy()
                    record.transform_keys(self._transform_keys)
                except AttributeError:
                    raise QueryError(f'Record `{record_name}` not found in '
                                     f'Query `{self.__NAME__}`.')

                rn[record_name] = record.get_required_fields(fields)
        else:
            for record_name in self.record_names:
                record_name = self.transform(record_name, False)
                record = getattr(self, record_name).copy()
                record.transform_keys(self._transform_keys)
                rn[record_name] = record.get_required_fields()

        return rn

    def resolve(self, records=None, **props):
        out = {}
        props = transform_deep_keys(props, self._transform_keys)
        required_records = self.get_required_records(records or {})

        #: Execute local plugins
        self.execute_plugins(records=required_records.copy(), **props)
        #: Executes the apply function which is meant to perform the actual
        #  query task
        data = None

        if hasattr(self, 'apply'):
            data = self.apply(records=required_records.copy(), **props)
            '''try:
                data = self.apply(records=required_records.copy(), **props)
            except (QueryErrors, ActionErrors) as e:
                return None
                return e.for_json()'''

        data = {} if data is None else data

        for record_name, fields in required_records.items():
            record = getattr(self, record_name).copy()
            record.transform_keys(self._transform_keys)
            record_name = self.transform(record_name)

            try:
                result = record.resolve(self, fields=fields, **data)
            except RecordIsNull:
                result = None
            #except (QueryErrors, ActionErrors) as e:
            #    return None
                # return e.for_json()

            out[record_name] = result

        try:
            return self.callback(self, out)
        except TypeError:
            return out

    def copy(self):
        cls = self.__class__(plugins=self.plugins, callback=self.callback)
        cls._transform_keys = self._transform_keys

        return cls
