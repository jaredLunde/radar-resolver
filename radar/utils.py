import re
from vital.tools import strings as string_tools


__all__ = ('to_js_keys', 'transform_keys')


js_keys_re = re.compile(r"""([^\\])"([A-Za-z]+[A-Za-z0-9_]*?)":""")


def to_js_keys(output):
    return js_keys_re.sub(r'\1\2:', output)


def to_snake(key):
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


def transform_keys(key, truthy_falsy, to_js=True):
    if truthy_falsy:
        camel = string_tools.camel_to_underscore(key) if to_js is False else\
                to_snake(key)

        return camel
    return key
