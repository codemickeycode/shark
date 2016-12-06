import inspect
from shark.base import Object, Default
from shark.common import iif


class ObjectInspector(object):
    def load(self, mod):
        objects = []
        functions = []
        filename = inspect.getfile(mod)

        for key in dir(mod):
            obj = getattr(mod, key)
            if inspect.isclass(obj) and issubclass(obj, Object) and key != 'Object' and inspect.getfile(obj)==filename:

                parameters = [p for p in inspect.signature(obj.__init__).parameters][1:]
                param_info = []

                def param(self, value, type, description, default=None):
                    name = parameters.pop(0)
                    param_info.append({
                        'name': name,
                        'type': type,
                        'description': description,
                        'default': iif(value == Default, default, value),
                        'class': iif(value == Default, default, value).__class__.__name__})
                    return old_param(self, value, type, description, default)

                # Using a custom param function to record the param info
                old_param = obj.param
                obj.param = param
                obj() #Create an instance to run our param recording
                obj.param = old_param
                code = inspect.getsourcelines(obj)
                objects.append((key, obj, param_info, code[0], code[1]))

            if inspect.isfunction(obj) and inspect.getfile(obj)==filename:
                functions.append((obj, inspect.signature(obj).parameters))

        objects.sort(key=lambda obj:obj[4])
        return objects


def trim_docstring(docstring):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = None
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            if not indent or len(line) - len(stripped) < indent:
                indent = len(line) - len(stripped)
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)
