from django.db.models import *
from django.utils.timezone import now


class SharkModel(Model):
    class Meta:
        abstract = True

    def __iter__(self):
        for field_name in self._meta.get_fields():
            yield field_name

    @classmethod
    def load(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None

    primary_field_name = None
    def __str__(self):
        if self.__class__.primary_field_name is None:
            for primary_field in ['name']:
                if primary_field in dir(self):
                    self.__class__.primary_field_name = primary_field
                    break

        if self.__class__.primary_field_name:
            return self.__getattribute__(self.__class__.primary_field_name)
        else:
            return super().__str__()


class EditableText(SharkModel):
    name = CharField(max_length=128, primary_key=True, unique=True)
    content = TextField()
    filename = CharField(max_length=1024)
    handler_name = CharField(max_length=512)
    line_nr = IntegerField()
    last_used = DateTimeField(default=now)