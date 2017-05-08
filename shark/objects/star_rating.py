from django.contrib.staticfiles.storage import staticfiles_storage
from shark.base import Object
from shark.param_converters import IntegerParam, BooleanParam


class StarRating(Object):
    def __init__(self, rating=None, readonly=False, **kwargs):
        self.init(kwargs)
        self.rating = self.param(rating, IntegerParam, 'Current rating.')
        self.readonly = self.param(readonly, BooleanParam, 'Is the rating read only?')
        self.id_needed()

    def get_html(self, html):
        html.append('<select' + self.base_attributes + '>')
        for i in range(1, 6):
            html.append('   <option value="{}"{}>{}</option>'.format(i, ' selected' if i==self.rating else '', i))
        html.append('</select>')

        html.append_js('$("#{}").barrating({{theme: "bootstrap-stars"{}}});'.format(self.id, ', readonly: true' if self.readonly else ''))

        html.add_resource(staticfiles_storage.url('shark/js/jquery.barrating.min.js'), 'js', 'star_rating', 'main')
        html.add_resource(staticfiles_storage.url('shark/css/rating-themes/bootstrap-stars.css'), 'css', 'star_rating', 'bootstrap')
