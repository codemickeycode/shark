import inspect
import shark
from shark.base import BaseObject, Default
from shark.common import iif


class ObjectInspector(object):
    def load(self, mod):
        objects = []
        filename = inspect.getfile(mod)

        for key in dir(mod):
            obj = getattr(mod, key)
            if inspect.isclass(obj) and issubclass(obj, BaseObject) and key != 'BaseObject' and inspect.getfile(obj)==filename:

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

        objects.sort(key=lambda obj:obj[4])
        return objects
