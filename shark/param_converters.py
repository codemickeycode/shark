from collections import Iterable

from django.db.models import Model
from django.db.models import QuerySet
from shark.actions import NoAction, URL, BaseAction, JS, Action
from shark.base import BaseParamConverter, Objects, Object
from shark.dependancies import escape_html, escape_url
from shark.objects.enumerations import ButtonStyle, Size, ButtonState, QuickFloat


class IntegerParam(BaseParamConverter):
    """
    Turns the value into an int
    None will remain None
    """
    @classmethod
    def convert(cls, value, parent_object):
        if value is not None:
            return int(value)

        return None


class FloatParam(BaseParamConverter):
    """
    Turns the value into a float
    None will remain None
    """
    @classmethod
    def convert(cls, value, parent_object):
        if value is not None:
            return float(value)

        return None


class BooleanParam(BaseParamConverter):
    """
    Converts any value into True or False
    Convertion is mainly done using the default pyhthon "if" statement, except:
    - The "false" string becomes False (case-insensitive)
    - The "none" string becomes False (case-insensitive)
    - The "0" string becomes False
    """
    @classmethod
    def convert(cls, value, parent_object):
        if isinstance(value, str) and value.lower() in ['false', 'none', '0']:
            return False

        return True if value else False


class ListParam(BaseParamConverter):
    @classmethod
    def convert(cls, value, parent_object):
        if value is None:
            return []
        elif isinstance(value, list):
            return value
        elif isinstance(value, Iterable) and not isinstance(value, str):
            return list(value)

        return [value]


class RawParam(BaseParamConverter):
    """
    Turns the value into a str without escaping
    """
    @classmethod
    def convert(cls, value, parent_object):
        if not value is None:
            if isinstance(value, str):
                return value
            else:
                return str(value)

        return ''


class UrlParam(BaseParamConverter):
    """
    Turns value into a URL object assuming that the passed in value is a url.
    Any BaseAction value gets returned untouched.
    """
    @classmethod
    def convert(cls, value, parent_object):
        if not value:
            return NoAction()
        elif isinstance(value, str):
            return URL(value)
        elif isinstance(value, BaseAction):
            return value
        else:
            return URL(str(value))


class QueryStringParam(BaseParamConverter):
    @classmethod
    def convert(cls, value, parent_object):
        if value is None:
            return ''

        if not isinstance(value, str):
            value = str(value)

        # Is this even the right escape function?
        return escape_url(value)


class CssAttributeParam(BaseParamConverter):
    @classmethod
    def convert(cls, value, parent_object):
        if value is None:
            return ''

        if not isinstance(value, str):
            value = str(value)

        # TODO: What about newlines? Do we need another escape function here?
        return escape_html(value)


class JavascriptParam(BaseParamConverter):
    """
    Turns value into a JS object assuming that the passed in value is a url.
    Any BaseAction value gets returned untouched.
    """
    @classmethod
    def convert(cls, value, parent_object):
        if not value:
            return NoAction()
        elif isinstance(value, str):
            return JS(value)
        elif isinstance(value, BaseAction):
            return value
        else:
            return JS(str(value))


class ActionParam(BaseParamConverter):
    """
    Turns value into an Action object assuming that the passed in value is a url.
    Any BaseAction value gets returned untouched.
    """
    @classmethod
    def convert(cls, value, parent_object):
        if not value:
            return NoAction()
        elif isinstance(value, str):
            return Action(value)
        elif isinstance(value, BaseAction):
            return value
        else:
            return Action(str(value))


class ObjectsParam(BaseParamConverter):
    """

    """
    @classmethod
    def convert(cls, value, parent_object):
        if not isinstance(value, Objects):
            value = Objects(value)

        value._parent = parent_object

        return value


class ModelParam(BaseParamConverter):
    @classmethod
    def convert(cls, value, parent_object):
        if value is None:
            return None
        if isinstance(value, Model):
            return value

        raise TypeError("Parameter isn't a Django Model object")


class DataTableParam(BaseParamConverter):
    @classmethod
    def convert(cls, value, parent_object):
        if value is None:
            return ([], [])
        elif isinstance(value, tuple) and len(value)>=2 and isinstance(value[0], list) and isinstance(value[1], list):
            return value
        elif isinstance(value, QuerySet):
            fields = value._fields
            return (
                fields,
                [[record[field_name] for field_name in fields] for record in value]
            )
        elif isinstance(value, Iterable) and not isinstance(value, str):
            fields = []
            data = []
            first_record = True
            record_transform_function = None
            for record in value:
                if first_record:
                    if isinstance(record, dict):
                        fields = [field_name for field_name in record]
                        record_transform_function = lambda r:  [r[field_name] for field_name in fields]
                    elif isinstance(record, Iterable) and not isinstance(record, str):
                        fields = [str(x) for x in range(len(record))]
                        record_transform_function = lambda r: [r[int(x)] for x in fields]
                    else:
                        raise TypeError("Parameter not in one of the accepted DataTable formats")

                    first_record = False

                data.append(record_transform_function(record))

            return (fields, data)

        raise TypeError("Parameter not in one of the accepted DataTable formats")
