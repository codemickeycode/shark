from shark.base import BaseObject
from shark.resources import Resources


class StarRating(BaseObject):
    def __init__(self, rating=None, readonly=False, **kwargs):
        self.init(kwargs)
        self.rating = self.param(rating, 'int', 'Current rating.')
        self.readonly = self.param(readonly, 'bool', 'Is the rating read only?')

    def get_html(self, html):
        html.append('<select' + self.base_attributes + '>')
        for i in range(1, 6):
            html.append('   <option value="{}"{}>{}</option>'.format(i, ' selected' if i==self.rating else '', i))
        html.append('</select>')

    def get_js(self):
        return '$("#{}").barrating({{theme: "bootstrap-stars"{}}});'.format(self.id, ', readonly: true' if self.readonly else '')


Resources.add_resource('/static/shark/js/jquery.barrating.min.js', 'js', 'star_rating', 'main')
Resources.add_resource('/static/shark/css/rating-themes/bootstrap-stars.css', 'css', 'star_rating', 'bootstrap')