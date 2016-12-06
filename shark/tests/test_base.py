from unittest import TestCase
from unittest import main

from shark.base import Enumeration, StringParam, Object, Objects, Text
from shark.common import Default
from shark.param_converters import ObjectsParam
from shark.renderer import Renderer


class MyEnumaration(Enumeration):
    first = 1
    second = 2
    last = 3


class TestEnumeration(TestCase):

    def test_get_value(self):
        self.assertEqual(MyEnumaration().second, 2, 'Looking up value failed')

    def test_value_map(self):
        self.assertEqual(MyEnumaration.value_map, {1: 'first', 2: 'second', 3: 'last'}, 'Value map wrong')

    def test_str_map(self):
        self.assertEqual(MyEnumaration.str_map, {'second': 2, 'first': 1, 'last': 3}, 'String map is wrong')

    def test_name(self):
        self.assertEqual(MyEnumaration.name(2), 'second', 'Name lookup failed')
        with self.assertRaises(ValueError, msg='Invalid name lookup does not raise ValueError'):
            MyEnumaration.name(4)

    def test_names(self):
        self.assertEqual(list(MyEnumaration.names()), ['first', 'second', 'last'], 'Names incorrect')

    def test_From_str(self):
        self.assertEqual(MyEnumaration.from_str('second'), 2, 'From_str failed')
        with self.assertRaises(ValueError, msg='Invalid string lookup does not raise ValueError'):
            MyEnumaration.from_str('wrong')


XSS_OPEN_BRACKET_VARIATIONS = [
    '<',
    '&lt',
    '&lt;',
    '&LT',
    '&LT;',
    '&#60',
    '&#060',
    '&#0060',
    '&#00060',
    '&#000060',
    '&#0000060',
    '&#60;',
    '&#060;',
    '&#0060;',
    '&#00060;',
    '&#000060;',
    '&#0000060;',
    '&#x3c',
    '&#x03c',
    '&#x003c',
    '&#x0003c',
    '&#x00003c',
    '&#x000003c',
    '&#x3c;',
    '&#x03c;',
    '&#x003c;',
    '&#x0003c;',
    '&#x00003c;',
    '&#x000003c;',
    '&#X3c',
    '&#X03c',
    '&#X003c',
    '&#X0003c',
    '&#X00003c',
    '&#X000003c',
    '&#X3c;',
    '&#X03c;',
    '&#X003c;',
    '&#X0003c;',
    '&#X00003c;',
    '&#X000003c;',
    '&#x3C',
    '&#x03C',
    '&#x003C',
    '&#x0003C',
    '&#x00003C',
    '&#x000003C',
    '&#x3C;',
    '&#x03C;',
    '&#x003C;',
    '&#x0003C;',
    '&#x00003C;',
    '&#x000003C;',
    '&#X3C',
    '&#X03C',
    '&#X003C',
    '&#X0003C',
    '&#X00003C',
    '&#X000003C',
    '&#X3C;',
    '&#X03C;',
    '&#X003C;',
    '&#X0003C;',
    '&#X00003C;',
    '&#X000003C;'
]

class TestStringParam(TestCase):
    def test_convert(self):
        self.assertEqual(StringParam.convert(None, None), '', 'Error converting None')
        self.assertEqual(StringParam.convert('Test', None), 'Test', 'Error converting None')
        self.assertEqual(StringParam.convert(123, None), '123', 'Error converting None')
        self.assertEqual(StringParam.convert([123], None), "[123]", 'Error converting None')

    def test_convert_escapes(self):
        self.assertEqual(StringParam.convert('<>', None), '&lt;&gt;', 'Did not protect against <>')
        self.assertEqual(StringParam.convert('\'"', None), '&#39;&quot;', 'Did not protect against quotes')
        self.assertEqual(StringParam.convert("'';!--\"<XSS>=&{()}", None), '&#39;&#39;;!--&quot;&lt;XSS&gt;=&amp;{()}', 'Did not protect against XSS')

        for text in XSS_OPEN_BRACKET_VARIATIONS:
            self.assertNotEqual(text, StringParam.convert(text, None))


class SimpleObject(Object):
    def __init__(self, **kwargs):
        self.init(kwargs)

    def get_html(self, renderer):
        renderer.append('Test')


class TestObject(TestCase):
    def test_id(self):
        obj = SimpleObject()
        self.assertEqual(obj._id, None)
        self.assertEqual(obj.id, 'SimpleObject_1')
        self.assertEqual(obj.id, 'SimpleObject_1')
        self.assertEqual(obj._id, 'SimpleObject_1')

        obj2 = SimpleObject(id='Custom_ID')
        self.assertEqual(obj2._id, 'Custom_ID')
        self.assertEqual(obj2.id, 'Custom_ID')

        obj3 = SimpleObject()
        self.assertEqual(obj3._id, None)
        self.assertEqual(obj3.id, 'SimpleObject_2')
        self.assertEqual(obj3.id, 'SimpleObject_2')
        self.assertEqual(obj3._id, 'SimpleObject_2')

    def test_param(self):
        obj = SimpleObject()
        self.assertEqual(obj.param(3, StringParam, 'Description'), '3')
        self.assertEqual(obj.param(Default, StringParam, 'Description', 3), '3')
        self.assertEqual(obj.param(Default, StringParam, 'Description', Default), Default)
        with self.assertRaises(TypeError):
            obj.param(3, 'string', 'Description')

    def test_get_html(self):
        obj = SimpleObject()
        renderer = Renderer()
        obj.get_html(renderer)
        self.assertEqual(renderer.html, 'Test\r\n')

    def test_operators(self):
        objs = SimpleObject() + 'Text'
        self.assertEqual(str(objs), '[<SimpleObject - None>, <Text - None>]')
        self.assertEqual(objs.__class__, Objects)
        for o in objs:
            self.assertEqual(o._parent, objs)

        objs = 'Text' + SimpleObject()
        self.assertEqual(str(objs), '[<Text - None>, <SimpleObject - None>]')
        self.assertEqual(objs.__class__, Objects)
        for o in objs:
            self.assertEqual(o._parent, objs)

    def test_objects_param(self):
        obj = SimpleObject()
        obj.id_needed()

        def iprint(value):
            print(value.__class__.__name__, value, value._parent)
            for o in value:
                print('-', o.__class__.__name__, o, o._parent)

        iprint(ObjectsParam.convert(None, obj))
        iprint(ObjectsParam.convert(123, obj))
        iprint(ObjectsParam.convert("Test", obj))
        iprint(ObjectsParam.convert([None, None], obj))
        iprint(ObjectsParam.convert([123, 456], obj))
        iprint(ObjectsParam.convert(["Test", "ing"], obj))
        iprint(ObjectsParam.convert(SimpleObject(), obj))
        iprint(ObjectsParam.convert([SimpleObject(), Text("Test")], obj))

        objs = Objects()
        objs += None
        objs += 123
        objs += "Test"
        objs += [None]
        objs += [123, 456]
        objs += ["Test", "ing"]
        objs += SimpleObject()
        objs += [SimpleObject(), Text("Test")]
        objs += [SimpleObject() + Text("Test")]

        iprint(objs)


class TestRenderer(TestCase):
    def test_renderer(self):
        renderer = Renderer()

        renderer.render('', Text("Test"))

        print('Output:')
        print('HTML', renderer.html)
        print('CSS', renderer.css)
        print('JS', renderer.js)
        print(renderer.js_files)
        print(renderer.js_resources)
        print(renderer.css_files)
        print(renderer.css_resources)


if __name__ == '__main__':
    main()