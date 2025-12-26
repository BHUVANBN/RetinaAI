from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter to get dictionary value by key"""
    return dictionary.get(key, '')

@register.filter
def sub(value, arg):
    """Subtract the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return ''

# Add intcomma filter if not already available
from django.contrib.humanize.templatetags.humanize import intcomma
register.filter('intcomma', intcomma)
