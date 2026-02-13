from django import template

register = template.Library()

@register.inclusion_tag('components/card.html')
def card(**kwargs):
    return kwargs

@register.inclusion_tag('components/table.html')
def table(**kwargs):
    return kwargs

@register.inclusion_tag('components/list.html')
def list_comp(**kwargs):
    return kwargs

@register.inclusion_tag('components/hero.html')
def hero(**kwargs):
    return kwargs
