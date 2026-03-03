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

@register.filter(name='is_media_widget')
def is_media_widget(field):
    """Checks if a form field's widget is a MediaPickerWidget."""
    try:
        return field.field.widget.__class__.__name__ == 'MediaPickerWidget'
    except AttributeError:
        return False

@register.filter(name='has_media_fields')
def has_media_fields(form):
    """Checks if a form has any MediaPickerWidget fields."""
    try:
        return any(f.field.widget.__class__.__name__ == 'MediaPickerWidget' for f in form.visible_fields())
    except Exception:
        return False

