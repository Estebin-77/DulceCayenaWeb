from django.shortcuts import get_object_or_404, render
from .models import Categoria, Producto


def tienda(request, categoria_slug=None):
    categorias = Categoria.objects.filter(activa=True).order_by("nombre")
    productos = Producto.objects.filter(disponible=True).select_related("categoria")
    destacados = Producto.objects.filter(disponible=True, destacado=True).select_related("categoria")[:4]
    categoria_actual = None

    if categoria_slug:
        categoria_actual = get_object_or_404(
            Categoria,
            slug=categoria_slug,
            activa=True
        )
        productos = productos.filter(categoria=categoria_actual)

    carrito = request.session.get("carrito", {})

    for producto in productos:
        producto.cant_en_carrito = carrito.get(str(producto.id), {}).get("cantidad", 0)

    for producto in destacados:
        producto.cant_en_carrito = carrito.get(str(producto.id), {}).get("cantidad", 0)

    return render(request, "tienda/tienda.html", {
        "productos": productos,
        "categorias": categorias,
        "categoria_actual": categoria_actual,
        "destacados": destacados,
    })


def detalle_producto(request, slug):
    producto = get_object_or_404(
        Producto.objects.select_related("categoria"),
        slug=slug,
        disponible=True
    )

    carrito = request.session.get("carrito", {})
    producto.cant_en_carrito = carrito.get(str(producto.id), {}).get("cantidad", 0)

    relacionados = Producto.objects.filter(
        disponible=True,
        categoria=producto.categoria
    ).exclude(id=producto.id)[:4]

    for item in relacionados:
        item.cant_en_carrito = carrito.get(str(item.id), {}).get("cantidad", 0)

    return render(request, "tienda/detalle_producto.html", {
        "producto": producto,
        "relacionados": relacionados,
    })