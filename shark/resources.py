import logging


class Resource(object):
    def __init__(self, url, type, module, name):
        self.url = url
        self.type = type
        self.module = module
        self.name = name


class Resources:
    def __init__(self):
        self.resources = []
        self.resource_map = {}

    def add_resource(self, url, type, module, name=''):
        key = '{}|{}|{}'.format(type, module, name)
        if not key in self.resource_map:
            resource = Resource(url, type, module, name)
            self.resources.append(resource)
            self.resource_map[key] = resource

    def replace_resource(self, url, type, module, name=''):
        key = '{}|{}|{}'.format(type, module, name)
        if key in self.resource_map:
            self.resource_map[key].url = url
        else:
            logging.warning('Resource {} cannot be found to be replaced. Added instead.'.format(key))
            self.add_resource(url, type, module, name)

