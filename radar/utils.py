import re
import json
from vital.cache import memoize
from vital.tools import strings as string_tools


__all__ = (
    'to_js_keys',
    'transform_keys',
    'to_js_shape',
    'get_class_attrs',
    'to_js_key',
    'to_python_key'
)


js_keys_re = re.compile(r"""([^\\])"([A-Za-z]+[A-Za-z0-9_]*?)":""")
js_records_re = re.compile(r"""(:\s*)(")([A-Za-z0-9_]*?.fields)(")""")


def to_js_keys(output):
    return js_records_re.sub(r'\1\3', js_keys_re.sub(r'\1\2:', output))


@memoize
def to_js_key(key):
    camel = list(string_tools.underscore_to_camel(key))
    next_char = 0

    while True:
        try:
            char = camel[next_char]
            if char == '_':
                next_char += 1
                continue
            if char.islower():
                break
            camel[next_char] = char.lower()
            break
        except IndexError:
            break

    return ''.join(camel)


@memoize
def to_python_key(key):
    return string_tools.camel_to_underscore(key)


def transform_keys(key, truthy_falsy, to_js=True):
    return string_tools.camel_to_underscore(key) if to_js is False else to_snake(key)


def to_js_shape(shape, indent):
    return '\n'.join(
        (' ' * indent) + line if idx > 0 else line
        for idx, line in
            enumerate(json.dumps(shape, indent=indent).split('\n'))
    )


def get_class_attrs(base_cls):
    for cls in reversed(base_cls.__mro__):
        if cls != type and cls != object:
            for items in cls.__dict__.items():
                yield items
