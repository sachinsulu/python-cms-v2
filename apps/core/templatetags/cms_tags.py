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


@register.filter(name='get_attr')
def get_attr(obj, attr_path):
    """
    Traverse dotted attribute paths on any object. Handles None gracefully.

    Usage in templates:
        {{ obj|get_attr:"author.username" }}
        {{ obj|get_attr:"get_package_type_display" }}   {# callable — called automatically #}
        {{ obj|get_attr:"is_active" }}
    """
    if obj is None or not attr_path:
        return None

    value = obj
    for part in str(attr_path).split('.'):
        try:
            value = getattr(value, part)
        except AttributeError:
            try:
                value = value[part]
            except (KeyError, TypeError, IndexError):
                return None
        # Call zero-argument callables (e.g. get_package_type_display)
        if callable(value) and not isinstance(value, type):
            try:
                value = value()
            except TypeError:
                pass  # leave as callable if it needs args
    return value