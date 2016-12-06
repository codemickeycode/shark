from shark.base import Enumeration


class Size(Enumeration):
    default = 0
    md = 1
    sm = 2
    xs = 3
    lg = 4


class ButtonStyle(Enumeration):
    default = 1
    primary = 2
    success = 3
    info = 4
    warning = 5
    danger = 6
    link = 7


class ButtonState(Enumeration):
    none = 0
    active = 1
    disabled = 2


class BackgroundColor(Enumeration):
    default = 0
    primary = 1
    success = 2
    info = 3
    warning = 4
    danger = 5

    @classmethod
    def name(cls, value):
        return ('bg-' + super().name(value)) if value else ''


class ContextualColor(BackgroundColor):
    muted = 6

    @classmethod
    def name(cls, value):
        return ('text-' + super().name(value).split('-')[-1]) if value else ''


class QuickFloat(Enumeration):
    default = 0
    left = 1
    right = 2

    @classmethod
    def name(cls, value):
        return ('pull-' + super().name(value)) if value else ''


