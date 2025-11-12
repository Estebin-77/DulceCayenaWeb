from django.shortcuts import render
from .models import Producto

def tienda(request):
    productos = Producto.objects.all()
    carrito = request.session.get("carrito", {})

    for producto in productos:
        producto.cant_en_carrito = carrito.get(str(producto.id), {}).get("cantidad", 0)

    return render(request, 'tienda/tienda.html', {
        "productos": productos
    })

