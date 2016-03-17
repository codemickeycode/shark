class Resource(object):
    def __init__(self, url, type, module, name):
        self.url = url
        self.type = type
        self.module = module
        self.name = name


class Resources:
    resources = []

    @classmethod
    def add_resource(cls, url, type, module, name=''):
        cls.resources.append(Resource(url, type, module, name))

    @classmethod
    def replace_resource(cls, url, type, module, name=''):
        for resource in cls.resources:
            if resource.module == module and resource.name == name and resource.type == type:
                resource.url = url
                return

        raise NameError("Resource not found.")