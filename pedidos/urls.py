from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [
    path('confirmar/', views.confirmar_pedido, name='confirmar'),
    path('exito/<int:pedido_id>/', views.exito, name='exito'),
    path('descargar-pdf/<int:pedido_id>/', views.descargar_pdf, name='descargar_pdf'),
]

