# servicios/urls.py
from django.urls import path
from . import views

app_name = "servicios"

urlpatterns = [
    path("", views.lista_servicios, name="lista"),
    path("<slug:slug>/", views.detalle_servicio, name="detalle"),
    path("<slug:slug>/solicitar/", views.solicitar_servicio, name="solicitar_servicio"),
    path("<slug:slug>/gracias/", views.gracias, name="gracias"),
]

