from radar.fields.field import Field
from radar.members import Members
from radar.exceptions import FieldNotFound
from radar.utils import transform_keys


def obj_resolver(obj_field):
    def resolver(query=None, node=None, fields=None, **data):
        fields = fields or []
        return obj_field.set_value({
            transform_keys(field.name, node._transform_keys):
                field.resolve(query=query, node=node, fields=fields, **data)
            for field in obj_field.get_fields(*fields)
        })
    return resolver


class Obj(Field, Members):

    def __init__(self, not_null=False, default=None, cast=None):
        cast = cast or dict
        super().__init__(obj_resolver, key=False, not_null=not_null,
                         default=default, cast=cast)
        self.resolver = obj_resolver(self)
        self.fields = []
        self._compile()

    def _compile(self):
        """ Sets :class:Field attributes """
        add_field = self.fields.append
        set_field = self.__setattr__

        for field_name, field in self._getmembers():
            if isinstance(field, Field):
                field = field.copy()
                field.name = field_name
                add_field(field)
                set_field(field_name, field)

    def get_fields(self, *fields):
        if not fields:
            for field in self.fields:
                yield field
        else:
            for field_name in fields:
                field = getattr(self, field_name)
                if field in self.fields:
                    yield field
                else:
                    raise FieldNotFound(f'Field "{field}" was not found in '
                                        f'the object "{self.name}"')

    def resolve(self, query=None, **data):
        return self.set_value(self.resolver(query=query, **data))

    def copy(self):
        return self.__class__(not_null=self.not_null,
                              default=self.default,
                              cast=self.cast)
