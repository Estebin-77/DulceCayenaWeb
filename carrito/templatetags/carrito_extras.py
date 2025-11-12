from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica dos valores numéricos."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_total_carrito(carrito):
    """Suma el total del carrito."""
    total = 0
    for item in carrito.values():
        total += float(item['precio']) * item['cantidad']
    return total

@register.filter
def get_item(dict_data, key):
    """Obtiene un valor del dict usando el id como clave."""
    try:
        return dict_data.get(int(key), 0)
    except:
        return 0
