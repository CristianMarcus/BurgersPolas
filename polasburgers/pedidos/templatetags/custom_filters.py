from django import template

register = template.Library()

@register.filter(name='multiplicar')
def multiplicar(value, arg):
    return value * arg