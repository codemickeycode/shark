from django.contrib import admin

from shark.models import EditableText

@admin.register(EditableText)
class EditableTextAdmin(admin.ModelAdmin):
    list_display = ['name', 'handler_name', 'last_used']
    list_filter = ['last_used', 'handler_name']
    ordering = ['handler_name', 'name']

