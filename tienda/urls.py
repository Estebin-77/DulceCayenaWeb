from django.urls import path
from . import views
from carrito import views as carrito_views

urlpatterns = [
    path('', views.tienda, name='tienda'),
    path('agregar/<int:producto_id>/', carrito_views.agregar_al_carrito, name='agregar_al_carrito'),
]
