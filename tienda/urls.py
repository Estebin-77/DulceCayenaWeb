from django.urls import path
from . import views
from carrito import views as carrito_views

app_name = "tienda"

urlpatterns = [
    path("", views.tienda, name="tienda"),
    path("categoria/<slug:categoria_slug>/", views.tienda, name="tienda_por_categoria"),
    path("producto/<slug:slug>/", views.detalle_producto, name="detalle_producto"),

    path("agregar/<int:producto_id>/", carrito_views.agregar_al_carrito, name="agregar_al_carrito"),
]