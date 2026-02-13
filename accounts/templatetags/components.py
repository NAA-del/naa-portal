from django import template

register = template.Library()

@register.inclusion_tag('components/card.html')
def card(**kwargs):
    return kwargs
