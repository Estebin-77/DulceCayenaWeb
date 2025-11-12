# servicios/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Servicio, SolicitudServicio
from .forms import SolicitudServicioForm

def lista_servicios(request):
    servicios = Servicio.objects.filter(activo=True)\
        .only("id","titulo","slug","precio_desde","imagen","descripcion")
    return render(request, "servicios/lista.html", {"servicios": servicios})

def detalle_servicio(request, slug):
    servicio = get_object_or_404(Servicio, slug=slug, activo=True)
    form = SolicitudServicioForm()
    action_url = reverse("servicios:solicitar_servicio", kwargs={"slug": servicio.slug})
    return render(request, "servicios/detalle.html", {
        "servicio": servicio,
        "form": form,
        "action_url": action_url,
    })

def solicitar_servicio(request, slug):
    servicio = get_object_or_404(Servicio, slug=slug, activo=True)
    if request.method != "POST":
        return redirect("servicios:detalle", slug=servicio.slug)

    form = SolicitudServicioForm(request.POST)
    if not form.is_valid():
        # Re-render con errores visibles y detalles del servicio
        action_url = reverse("servicios:solicitar_servicio", kwargs={"slug": servicio.slug})
        return render(request, "servicios/detalle.html", {
            "servicio": servicio,
            "form": form,
            "action_url": action_url,
        })

    # ✅ Guardar la solicitud
    solicitud: SolicitudServicio = form.save(commit=False)
    solicitud.servicio = servicio
    solicitud.save()

    # (Opcional) mensaje flash si luego quieres volver al detalle en vez de “gracias”
    messages.success(request, "¡Solicitud enviada! Te contactaremos pronto.")

    # ✅ Redirigir a la página de confirmación
    return redirect("servicios:gracias", slug=servicio.slug)

def gracias(request, slug):
    servicio = get_object_or_404(Servicio, slug=slug, activo=True)
    return render(request, "servicios/gracias.html", {"servicio": servicio})


