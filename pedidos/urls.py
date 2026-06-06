from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [
    path("confirmar/", views.confirmar_pedido, name="confirmar"),
    path("exito/<uuid:token_acceso>/", views.exito, name="exito"),
    path("descargar-pdf/<uuid:token_acceso>/", views.descargar_pdf, name="descargar_pdf"),
    path("consultar/", views.consultar_pedido, name="consultar_pedido"),
    path("detalle/<uuid:token_acceso>/", views.detalle_publico, name="detalle_publico"),

    path("panel/pedidos/", views.panel_pedidos, name="panel_pedidos"),
    path("panel/pedidos/<int:pedido_id>/", views.panel_pedido_detalle, name="panel_pedido_detalle"),
    path("panel/pedidos/<int:pedido_id>/cambiar-estado/", views.cambiar_estado_pedido, name="cambiar_estado_pedido"),
]
