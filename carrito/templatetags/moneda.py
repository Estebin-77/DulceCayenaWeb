from django import template

register = template.Library()

@register.filter(name='moneda')
def moneda(value):
    """
    Convierte un número a formato RD$ con coma para miles y punto para decimales.
    Ejemplo: 1250.75 -> RD$1,250.75
    Maneja strings y valores nulos sin romper la vista.
    """
    try:
        # Intentar convertir el valor a float
        value = float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        # Si no se puede convertir, devolver el valor original
        return value

    # Formatear el número con separadores de miles y dos decimales
    return f"RD${value:,.2f}"

