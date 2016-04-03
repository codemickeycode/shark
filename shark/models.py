import inspect

from django.conf.urls import url
from django.db.models import *
from django import forms
from django.http import Http404
from django.utils.timezone import now
from django.conf import settings
from django.conf import urls
from shark.widgets import MarkdownWidget


class SharkModel(Model):
    class Meta:
        abstract = True

    def __iter__(self):
        for field_name in self._meta.get_fields():
            yield field_name

    @classmethod
    def load(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None

    @classmethod
    def load_by_url_name(cls, url_name, raise_404_on_not_found=True):
        value = cls.objects.filter(url_name=url_name).first()
        if raise_404_on_not_found and not value:
            raise Http404()
        return value

    primary_field_name = None
    def __str__(self):
        if self.__class__.primary_field_name is None:
            for primary_field in ['name']:
                if primary_field in dir(self):
                    self.__class__.primary_field_name = primary_field
                    break

        if self.__class__.primary_field_name:
            return self.__getattribute__(self.__class__.primary_field_name)
        else:
            return super().__str__()


class EditableText(SharkModel):
    name = CharField(max_length=128, primary_key=True, unique=True)
    content = TextField()
    handler_name = CharField(max_length=512)
    last_used = DateTimeField(default=now)


class MarkdownFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        # Django admin overrides the 'widget' value so this seems the only way
        # to scupper it!
        super(MarkdownFormField, self).__init__(*args, **kwargs)
        self.widget = MarkdownWidget()


class MarkdownField(TextField):
    def formfield(self, **kwargs):
        defaults = {'form_class': MarkdownFormField}
        defaults.update(kwargs)
        return super(MarkdownField, self).formfield(**defaults)


class StaticPage(SharkModel):
    url_name = CharField(verbose_name='URL name', max_length=128, primary_key=True, unique=True)
    title = CharField(verbose_name='Page Title', max_length=512, null=True)
    description = CharField(verbose_name='Meta description', max_length=512, null=True)
    body = MarkdownField(verbose_name='Page Markdown Content', null=True)
    sitemap = BooleanField(verbose_name='Include in SiteMap?', default=True)
    robots_index = BooleanField(verbose_name='robots.txt index?', default=True)
    robots_follow = BooleanField(verbose_name='robots.txt follow?', default=True)

    def get_absolute_url(self):
        from .handler import StaticPage as StaticPageHandler
        return StaticPageHandler.url(self.url_name)


class Log(SharkModel):
    created = DateTimeField(default=now)
    url = CharField(max_length=1024)
    referrer = CharField(max_length=1024, blank=True)
    user_agent = CharField(max_length=1024, blank=True)
    ip_address = GenericIPAddressField()

