import logging


class Resource(object):
    def __init__(self, url, type, module, name):
        self.url = url
        self.type = type
        self.module = module
        self.name = name


class Resources:
    resources = []
    resource_map = {}

    @classmethod
    def add_resource(cls, url, type, module, name=''):
        key = '{}|{}|{}'.format(type, module, name)
        if not key in cls.resource_map:
            resource = Resource(url, type, module, name)
            cls.resources.append(resource)
            cls.resource_map[key] = resource

    @classmethod
    def replace_resource(cls, url, type, module, name=''):
        key = '{}|{}|{}'.format(type, module, name)
        if key in cls.resource_map:
            cls.resource_map[key].url = url
        else:
            logging.warning('Resource {} cannot be found to be replaced. Added instead.'.format(key))
            cls.add_resource(url, type, module, name)