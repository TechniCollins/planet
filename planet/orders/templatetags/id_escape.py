from django import template

register = template.Library()

@register.simple_tag
def idEscape(obj, attribute):
    return obj.get(attribute)
