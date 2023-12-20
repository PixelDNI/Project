from django import template

register = template.Library()

@register.filter
def get_value(value, key):
    if isinstance(value, str):
        value = template.Variable(value).resolve({})

    return value.get(key)

register = template.Library()

@register.filter
def get_dict_value(dictionary, key):
    return dictionary.get(key)


@register.filter
def make_list(value):
    value = value.replace("{", "").replace("}", "")  # Remove opening and closing brackets
    value_list = value.split(",")  # Split the string by comma
    values = [item.split(":")[1].strip() or "''" for item in value_list]  # Extract values with or without quotation marks
    return values


