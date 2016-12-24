from django.utils.html import escape
from django.utils.http import urlquote

escape_html = escape
def escape_url(url):
    return urlquote(url, safe=':/@?=')
