from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [
    path("confirmar/", views.confirmar_pedido, name="confirmar"),
    path("exito/<int:pedido_id>/", views.exito, name="exito"),
    path("descargar-pdf/<int:pedido_id>/", views.descargar_pdf, name="descargar_pdf"),
    path("consultar/", views.consultar_pedido, name="consultar_pedido"),
    path("detalle/<int:pedido_id>/", views.detalle_publico, name="detalle_publico"),

    path("panel/pedidos/", views.panel_pedidos, name="panel_pedidos"),
    path("panel/pedidos/<int:pedido_id>/", views.panel_pedido_detalle, name="panel_pedido_detalle"),
    path("panel/pedidos/<int:pedido_id>/cambiar-estado/", views.cambiar_estado_pedido, name="cambiar_estado_pedido"),
]