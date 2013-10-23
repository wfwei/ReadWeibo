from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter
def add_prefix(value, arg):
    """add some prefix for the given string"""
    return arg + str(value)

@register.filter
def get_range(value):
    '''return a list [0,value-1]'''
    return range(value)

@register.filter
def keyvalue(dict, key):
    ''' return dict keyvalue'''
    return dict[key]

@register.filter
def sp_category(categories, category_id):
    ''' return dict keyvalue'''
    for category in categories:
        if category.category_id == category_id:
            return category.name 
    return 'INVALID'

@register.filter
def parse_html_tag(value):
    ''' for '<a href="url">text</a>' return ('url', 'text') '''
    return value
#     res = re.search('<a.*?href="([^"]*)"[^>]*?>(.*?)</a>', value)
#     return (res.groups()[0], res.groups[1])
