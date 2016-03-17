import json

from django.utils.html import escape


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if 'serializable_object' in dir(o):
            return o.serializable_object()

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)


def js_action(action, **kwargs):
    json_params = ExtendedJSONEncoder().encode(kwargs)
    return u'do_action(\'' + escape(action) + '\', ' + escape(json_params) + u');return false;'

