import json
from vital.debug import preprX

from .exceptions import MissingApplyMethod
from .fields import Field
from .utils import to_js_keys, to_js_shape, get_class_attrs


__all__ = 'get_fields',


JS_TPL = '''import {{createInterface}} from 'react-radar'

export default createInterface({{
  name: '{name}',
  fields: {shape}
}})'''


def get_fields(attrs):
    for k, v in attrs.items():
        field = attrs[k]
        is_interface = hasattr(field, '__is_radar_interface__')

        if is_interface or isinstance(attrs[k], Field):
            field.__NAME__ = k
            yield field


class MetaInterface(type):
    def __new__(cls, name, bases, attrs):
        attrs['fields'] = tuple(get_fields(attrs))
        return super().__new__(cls, name, bases, attrs)


class Interface(object, metaclass=MetaInterface):
    __slots__ = tuple()
    __repr__ = preprX('fields', address=False)
    __is_radar_interface__ = True

    def __new__(cls, *a, **kw):
        interface = super().__new__(cls)
        interface.__init__(*a, **kw)
        interface.fields = tuple(
            field
            for k, v in get_class_attrs(interface.__class__)
            if k == 'fields'
            for field in v
        )
        return interface

    def copy(self):
        return self.__class__()

    def to_js(self, indent=2, plugins=None):
        shape = {}

        for field in self.fields:
            if isinstance(field, self.__class__):
                shape[field.__NAME__] = field.to_js()
            else:
                shape[field.__NAME__] = field.default

        if plugins:
            for plugin in plugins:
                shape = plugin(shape)

        output = JS_TPL.format(name=self.__class__.__name__,
                               shape=to_js_shape(shape, indent))

        return to_js_keys(output)


'''
from radar import Interface, fields

class MyInterface(Interface):
    foo = fields.String(key=True)
    bar = fields.Int()

class MySubInterface(MyInterface):
    baz = fields.Array()

MySubInterface()

from vital.debug import Timer
Timer(MySubInterface).time(1E5)
'''
