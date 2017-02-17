import re


__all__ = ('to_js_keys',)


js_keys_re = re.compile(r"""([^\\])"([A-Za-z]+[A-Za-z0-9_]*?)":""")


def to_js_keys(output):
    return js_keys_re.sub(r'\1\2:', output)
