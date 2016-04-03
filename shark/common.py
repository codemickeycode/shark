#TODO: Is there a Django version of this?
from collections import Iterable

from django.http import Http404


def safe_url(url):
    return url.replace('<', '').replace('>', '').replace('"', '').replace("'", '')

def iif(condition, value_true, value_false=''):
    return value_true if condition else value_false

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]

def listify(obj):
    """
    Turn anything that isn't iterable into a list, except str. None or '' become an empty list [], objects will become a single item list.
    """
    if not obj:
        return []
    if isinstance(obj, Iterable) and not isinstance(obj, str):
        return obj
    else:
        return [obj]


def first_or_404(model, **kwargs):
    obj = model.objects.filter(**kwargs).first()
    if obj is None:
        raise Http404()
    return obj

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."