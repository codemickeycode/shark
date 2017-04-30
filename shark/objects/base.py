from shark.base import Object
from shark.param_converters import RawParam, JavascriptParam


class Raw(Object):
    """
    Raw html to be rendered. This text will not be escaped.
    Be careful with using this as it can lead to security issues.
    """
    def __init__(self, text='', **kwargs):
        self.init(kwargs)
        self.text = self.param(text, RawParam, 'Raw text')

    def get_html(self, html):
        html.append(self.text)

    def __str__(self):
        return self.text or ''

    @classmethod
    def example(cls):
        return Raw('<b>Hello world!</b>')


class Script(Object):
    def __init__(self, script=None, **kwargs):
        self.init(kwargs)
        self.script = self.param(script, JavascriptParam, 'Javascript to execute')

    def get_html(self, renderer):
        renderer.append_js(self.script.js(renderer))
