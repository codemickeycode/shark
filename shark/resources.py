import logging


class Resource(object):
    def __init__(self, url, type, module, name):
        self.url = url
        self.type = type
        self.module = module
        self.name = name


class Resources(list):
    def __init__(self):
        super().__init__()
        self.map = {}

    def add_resource(self, url, type, module, name=''):
        key = '{}|{}|{}'.format(type, module, name)
        if not key in self.map:
            resource = Resource(url, type, module, name)
            self.append(resource)
            self.map[key] = resource

    def replace_resource(self, url, type, module, name=''):
        key = '{}|{}|{}'.format(type, module, name)
        if key in self.map:
            self.map[key].url = url
        else:
            logging.warning('Resource {} cannot be found to be replaced. Added instead.'.format(key))
            self.add_resource(url, type, module, name)

    def add_or_replace_resource(self, url, type, module, name=''):
        key = '{}|{}|{}'.format(type, module, name)
        if key in self.map:
            self.map[key].url = url
        else:
            self.add_resource(url, type, module, name)

    def add_resources(self, resources):
        for resource in resources:
            self.add_or_replace_resource(resource.url, resource.type, resource.module, resource.name)

