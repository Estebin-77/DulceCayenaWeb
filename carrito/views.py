from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from pedidos.forms import PedidoClienteForm
from tienda.models import Producto
from .carrito import Carrito


def es_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def agregar_al_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.agregar(producto)

    if es_ajax(request):
        return JsonResponse({"ok": True})

    # ✅ Volver a la misma URL desde donde se llamó
    return redirect(request.META.get("HTTP_REFERER", "carrito:ver_carrito"))

def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.restar(producto)

    if es_ajax(request):
        return JsonResponse({"ok": True})

    return redirect(request.META.get("HTTP_REFERER", "carrito:ver_carrito"))


def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    carrito.eliminar(producto)

    if es_ajax(request):
        return JsonResponse({"ok": True})

    return redirect(request.META.get("HTTP_REFERER", "carrito:ver_carrito"))



def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()

    if es_ajax(request):
        return JsonResponse({"ok": True})

    return redirect("tienda:tienda")


def ver_carrito(request):
    carrito = request.session.get("carrito", {})
    
    if not carrito:
        return render(request, "carrito/carrito_vacio.html")

    carrito_obj = Carrito(request)
    total = carrito_obj.total()

    return render(request, "carrito/carrito.html", {
        "carrito": carrito_obj.carrito,
        "total": total
    })

def checkout(request):
    carrito = Carrito(request)

    return render(request, "carrito/checkout.html", {
        "carrito": carrito.carrito,  # ✅ Agregado
        "items": carrito.carrito.values(),
        "total": carrito.total(),
    })




def cantidad_carrito(request):
    carrito = request.session.get("carrito", {})
    total_cantidad = sum(item["cantidad"] for item in carrito.values())
    return JsonResponse({"cantidad": total_cantidad})

