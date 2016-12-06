import pygments
import pygments.lexers
import pygments.formatters
from shark.base import StringParam

from shark.handler import Object
from shark.param_converters import RawParam


class HighlightCode(Object):
    """
    Highlight source code using the Python pygments library.
    """
    def __init__(self, code='', language='html', **kwargs):
        self.init(kwargs)
        self.code = self.param(code, RawParam, 'The code')
        self.language = self.param(language, StringParam, 'Language to use for highlighting')

    def get_html(self, html):
        code = pygments.highlight(
            self.code,
            pygments.lexers.get_lexer_by_name(self.language),
            pygments.formatters.get_formatter_by_name('html', noclasses=True)
        )
        html.append(code)

    @classmethod
    def example(self):
        return HighlightCode("<a href='http://google.com'>Google.com</a>")

