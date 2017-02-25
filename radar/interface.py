import json
from vital.debug import preprX

from radar.fields import Field
from radar.members import Members
from radar.utils import to_js_keys


JS_TPL = '''const {name} = Maestro.createInterface({
  name: '{name}',
  fields: {shape}
})'''


class Interface(Members):

    def __init__(self):
        """ @many: will return #list if @many is |True|
        """
        self.__NAME__ = self.__NAME__ if hasattr(self, '__NAME__') else \
                        self.__class__.__name__
        self._fields = []
        self._compile()

    __repr__ = preprX('__NAME__', 'fields', address=False)

    def _compile(self):
        """ Sets :class:Field attributes """
        for field_name, field in self._getmembers():
            if isinstance(field, (Field, Interface)):
                self.add_field(field_name, field)

    def add_field(self, field_name, field):
        field = field.copy()
        field.__NAME__ = field_name
        self._fields.append(field)
        setattr(self, field_name, field)

    @property
    def fields(self):
        return self._fields

    def to_js(self, indent=2, plugins=None):
        shape = {}

        for field in self._fields:
            if isinstance(field, self.__class__):
                shape[field.__NAME__] = field.to_js()
            else:
                shape[field.__NAME__] = field.default

        if plugins:
            for plugin in plugins:
                shape = plugin(shape)

        output = JS_TPL.format(name=self.__NAME__,
                               shape=json.dumps(shape, indent=indent))

        return to_js_keys(output)

    def copy(self):
        return self.__class__()
