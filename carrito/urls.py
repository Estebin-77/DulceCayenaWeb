# carrito/urls.py
from django.urls import path
from . import views

app_name = "carrito"

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('restar/<int:producto_id>/', views.restar_producto, name='restar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('cantidad/', views.cantidad_carrito, name='cantidad_carrito'),
]
