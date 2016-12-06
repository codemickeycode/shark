import re

import bleach
from markdown import markdown
from shark.base import Object, BaseParamConverter
from shark.common import LOREM_IPSUM
from shark.param_converters import RawParam

ALLOWED_TAGS = ['ul', 'ol', 'li', 'p', 'pre', 'code', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br', 'strong', 'em', 'a', 'img', 'div', 'span']

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'title', 'alt'],
    'div': ['style'],
    'span': ['style']
}

ALLOWED_STYLES = ['color', 'font-weight']


class Markdown(Object):
    """
    Render text as markdown. Shark objects can be rendered inside the markup with {{ }} tags
    and they are passed in through the keyword arguments.

    Several extensions are available:

    - markdown.extensions.codehilite
    - markdown.extensions.fenced_code
    - markdown.extensions.abbr
    - markdown.extensions.def_list
    - markdown.extensions.footnotes
    - markdown.extensions.tables
    - markdown.extensions.smart_strong
    - markdown.extensions.sane_lists
    - markdown.extensions.smarty
    - markdown.extensions.toc
    """
    def __init__(self, text='', **kwargs):
        self.init(kwargs)
        self.text = self.param(text, RawParam, 'Text to render as markdown')
        self.context = kwargs

    def get_html(self, html):
        extensions = [
            'markdown.extensions.codehilite',
            'markdown.extensions.fenced_code',
            'markdown.extensions.abbr',
            'markdown.extensions.def_list',
            'markdown.extensions.footnotes',
            'markdown.extensions.tables',
            'markdown.extensions.smart_strong',
            'markdown.extensions.sane_lists',
            'markdown.extensions.smarty',
            'markdown.extensions.toc'
        ]

        dirty = markdown(text=self.text, output_format='html5', extensions=extensions, extension_configs={
            'markdown.extensions.codehilite': {'css_class': 'highlight', 'noclasses': True}
        })
        clean = bleach.clean(dirty, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)
        for match in re.finditer('{{(.*?)}}', clean):
            arg_name = match.group(1).strip()
            if arg_name in self.context:
                raw = html.render_string(self.context[arg_name])
            else:
                raw = arg_name
            clean = re.sub(match.group(0), raw, clean)

        html.append(clean)

    @classmethod
    def example(self):
        from shark.objects.layout import Panel

        return Markdown(
            "###Markdown is great###\n"
            "Many different styles are available through MarkDown:\n\n"
            "1. You can make text **bold**\n"
            "2. Or *italic*\n"
            "3. And even ***both***\n"
            "\n"
            "You can include shark objects:\n"
            "{{ panel }}"
            "\n"
            "Read more about markdown [here](http://markdown.org)",
            panel = Panel(
                header='Just a panel',
                items=LOREM_IPSUM
            )
        )


class MarkdownParam(BaseParamConverter):
    @classmethod
    def convert(cls, value, parent_object):
        if not isinstance(value, Markdown):
            value = Markdown(value)

        value._parent = parent_object
        return value
