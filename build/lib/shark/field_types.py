from django.utils.translation import ugettext as _
from django.db.models import SmallIntegerField

DAY_OF_THE_WEEK = {
    1: _('Monday'),
    2: _('Tuesday'),
    3: _('Wednesday'),
    4: _('Thursday'),
    5: _('Friday'),
    6: _('Saturday'),
    7: _('Sunday'),
}

class DayOfTheWeek:
    def __init__(self, day_of_the_week):
        if isinstance(day_of_the_week, int):
            if day_of_the_week in DAY_OF_THE_WEEK:
                self.day_of_the_week = day_of_the_week
            else:
                raise KeyError('{} not an acceptable value for DayOfTheWeek (1-7)'.format(day_of_the_week))
        else:
            raise TypeError("DayOfTheWeek expects an integer (1-7). Got {}.".format(day_of_the_week.__class__.__name__))

    def __str__(self):
        return DAY_OF_THE_WEEK[self.day_of_the_week]

    def __repr__(self):
        return 'DayOfTheWeek({})'.format(DAY_OF_THE_WEEK[self.day_of_the_week])


class DayOfTheWeekField(SmallIntegerField):

    description = "Day of the Week"

    def __init__(self, *args, **kwargs):
        kwargs['choices']=tuple(sorted(DAY_OF_THE_WEEK.items()))
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['choices']
        return name, path, args, kwargs


class DayOfTheWeekFieldOld(SmallIntegerField):

    description = "Day of the Week"

    def __init__(self, *args, **kwargs):
        kwargs['choices']=tuple(sorted(DAY_OF_THE_WEEK.items()))
        super(DayOfTheWeekField,self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['choices']
        return name, path, args, kwargs

    def to_python(self, value):
        if value is not None:
            return DayOfTheWeek(value)
        return value

    def get_prep_value(self, value):
        if value is not None:
            if isinstance(value, DayOfTheWeek):
                return value.day_of_the_week
            elif not isinstance(value, int):
                raise TypeError("Value for DayOfTheWeekField must be int or DayOfTheWeek. Got %r." % value)
        return value

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

