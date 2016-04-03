from django.contrib import admin
from django.http import HttpResponseRedirect

from shark.models import EditableText, StaticPage


@admin.register(EditableText)
class EditableTextAdmin(admin.ModelAdmin):
    list_display = ['name', 'handler_name', 'last_used']
    list_filter = ['last_used', 'handler_name']
    ordering = ['handler_name', 'name']

    fieldsets = (
        (None, {
            'fields': ('name', 'handler_name')
        }),
        ('Content', {
            'fields': ('content',),
            'description': 'Enter the content for this text.'
        })
    )


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['url_name', 'title']
    ordering = ['url_name']

    def response_post_save_add(self, request, obj):
        from .handler import StaticPage as StaticPageHandler
        return HttpResponseRedirect(StaticPageHandler.url(obj.url_name))

    def response_post_save_change(self, request, obj):
        from .handler import StaticPage as StaticPageHandler
        return HttpResponseRedirect(StaticPageHandler.url(obj.url_name))
