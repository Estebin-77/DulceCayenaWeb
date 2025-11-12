from django.conf import settings
from django.conf.urls.static import static  
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Apps
    path('', include('inicio.urls')),
    path('servicios/', include(('servicios.urls', 'servicios'), namespace='servicios')),
    path('tienda/', include(('tienda.urls', 'tienda'), namespace='tienda')),
    path('contacto/', include('contacto.urls')),
    path('blog/', include('blog.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('carrito/', include(('carrito.urls', 'carrito'), namespace='carrito')),
]

# ✅ Esto permite ver las imágenes y archivos multimedia mientras estás en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)