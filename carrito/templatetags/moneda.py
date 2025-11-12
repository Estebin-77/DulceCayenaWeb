from django import template

register = template.Library()

@register.filter(name='moneda')
def moneda(value):
    """
    Convierte un número a formato RD$ con coma para miles y punto para decimales.
    Ejemplo: 1250.75 -> RD$1,250.75
    """
    try:
        value = float(value)
        return f"RD${value:,.2f}"
    except (ValueError, TypeError):
        return value

