from maestro.fields.field import Field
from maestro.members import Members
from maestro.exceptions import FieldNotFound


def obj_resolver(obj_field, node, fields):
    fields = fields or []
    return obj_field.set_value({
        field.name: field.resolve(node)
        for field in obj_field.get_fields(*fields)
    })


class Obj(Field, Members):

    def __init__(self, not_null=False, default=None, cast=None):
        cast = cast or dict
        super().__init__(obj_resolver, key=False, not_null=not_null,
                         default=default, cast=cast)
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

    def resolve(self, node, fields=None):
        return self.set_value(self.resolver(self, node, fields))

    def copy(self):
        return self.__class__(not_null=self.not_null,
                              default=self.default,
                              cast=self.cast)
