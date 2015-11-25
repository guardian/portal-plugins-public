from django import template
from django.utils.safestring import mark_safe
import urlparse

register = template.Library()

def is_absolute(url):
    return bool(urlparse.urlparse(url).netloc)

@register.filter("image_url")
def image_url(value, kls="smallicon"):
    if is_absolute(value):
        return mark_safe(value)

    return mark_safe(u'<span><img src="{s}" class="{k}">{s}</span>'.format(s=value, k=kls))
