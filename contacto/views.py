from django.shortcuts import render, redirect
from django.contrib import messages

def contacto(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        asunto = request.POST.get("asunto")
        mensaje = request.POST.get("mensaje")

        # En este punto, podríamos enviar un correo o guardar en base de datos (lo haremos luego)
        messages.success(request, f"Gracias {nombre}, tu mensaje ha sido enviado correctamente.")
        return redirect('contacto')

    return render(request, "contacto/contacto.html")
