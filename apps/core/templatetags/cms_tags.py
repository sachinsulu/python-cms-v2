from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """
    Splits a string by the given argument.
    Usage: {{ "a,b,c"|split:"," }} -> ["a", "b", "c"]
    """
    return value.split(arg)

@register.filter(name='getitem')
def getitem(dictionary, key):
    """
    Returns the value of a dictionary (or object with __getitem__) for a given key.
    Usage: {{ form|getitem:field_name }}
    """
    try:
        return dictionary[key]
    except (KeyError, TypeError, IndexError):
        # Also try getattr for objects
        try:
            return getattr(dictionary, key)
        except (AttributeError, TypeError):
            return None
