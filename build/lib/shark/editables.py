from django.utils.timezone import now

from shark.base import Text
from shark.models import EditableText


class EText(Text):
    def __init__(self, name='', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'text', 'Unique name for the text')

    def get_html(self, html):
        html.append('<span' + self.base_attributes + ' contenteditable="True" data-name="{}" onblur="content_changed(this);">'.format(self.name))
        html.append(self.term(self.name, html.handler) or '')
        html.append('</span>')
