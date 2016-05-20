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


