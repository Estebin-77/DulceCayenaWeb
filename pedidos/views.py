from datetime import date
from decimal import Decimal
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from .forms import PedidoClienteForm
from .models import HistorialEstadoPedido, LineaPedido, Pedido
from carrito.carrito import Carrito
from tienda.models import Producto


logger = logging.getLogger(__name__)


def es_staff(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(es_staff)
def panel_pedidos(request):
    q = request.GET.get("q", "").strip()
    estado_actual = request.GET.get("estado", "").strip()

    pedidos_qs = Pedido.objects.all()

    if q:
        pedidos_qs = pedidos_qs.filter(
            Q(nombre__icontains=q)
            | Q(email__icontains=q)
            | Q(id__icontains=q)
        )

    if estado_actual:
        pedidos_qs = pedidos_qs.filter(estado=estado_actual)

    paginator = Paginator(pedidos_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "pedidos": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "estado_actual": estado_actual,
        "estados": Pedido.Estado.choices,
        "total_resultados": paginator.count,
    }
    return render(request, "pedidos/panel_pedidos.html", context)


@login_required
@user_passes_test(es_staff)
def panel_pedido_detalle(request, pedido_id):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related(
            "lineas",
            Prefetch(
                "historial_estados",
                queryset=HistorialEstadoPedido.objects.select_related("cambiado_por"),
            ),
        ),
        pk=pedido_id,
    )

    estados_disponibles = []
    for value, label in Pedido.Estado.choices:
        if pedido.puede_cambiar_a(value):
            estados_disponibles.append((value, label))

    context = {
        "pedido": pedido,
        "lineas_pedido": pedido.lineas.all(),
        "historial_estados": pedido.historial_estados.all(),
        "estados_disponibles": estados_disponibles,
    }
    return render(request, "pedidos/panel_pedido_detalle.html", context)


@login_required
@user_passes_test(es_staff)
@require_POST
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    nuevo_estado = request.POST.get("estado", "").strip()
    nota = request.POST.get("nota", "").strip()

    estados_validos = {value for value, _ in Pedido.Estado.choices}

    if nuevo_estado not in estados_validos:
        messages.error(request, "El estado seleccionado no es válido.")
        return redirect("pedidos:panel_pedido_detalle", pedido_id=pedido.id)

    estado_anterior = pedido.estado

    if nuevo_estado == estado_anterior:
        messages.info(request, "El pedido ya se encuentra en ese estado.")
        return redirect("pedidos:panel_pedido_detalle", pedido_id=pedido.id)

    if not pedido.puede_cambiar_a(nuevo_estado):
        messages.error(
            request,
            f"No se permite cambiar un pedido de '{pedido.get_estado_display()}' "
            f"a '{dict(Pedido.Estado.choices).get(nuevo_estado, nuevo_estado)}'."
        )
        return redirect("pedidos:panel_pedido_detalle", pedido_id=pedido.id)

    pedido.estado = nuevo_estado
    pedido.save(update_fields=["estado"])

    HistorialEstadoPedido.objects.create(
        pedido=pedido,
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado,
        nota=nota,
        cambiado_por=request.user,
    )

    messages.success(
        request,
        f"Estado actualizado de {dict(Pedido.Estado.choices).get(estado_anterior)} "
        f"a {pedido.get_estado_display()}."
    )
    return redirect("pedidos:panel_pedido_detalle", pedido_id=pedido.id)


def consultar_pedido(request):
    codigo_inicial = request.GET.get("codigo", "").strip()
    email_inicial = request.GET.get("email", "").strip()
    datos_prefill = bool(codigo_inicial or email_inicial)

    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip()
        email = request.POST.get("email", "").strip().lower()

        if not codigo or not email:
            messages.error(request, "Debes completar el código del pedido y el correo electrónico.")
            return render(
                request,
                "pedidos/consultar_pedido.html",
                {
                    "codigo_inicial": codigo,
                    "email_inicial": request.POST.get("email", "").strip(),
                    "datos_prefill": False,
                },
            )

        pedidos = Pedido.objects.filter(email__iexact=email)

        pedido_encontrado = None
        for pedido in pedidos:
            if pedido.codigo_pedido.lower() == codigo.lower():
                pedido_encontrado = pedido
                break

        if pedido_encontrado:
            return redirect("pedidos:detalle_publico", pedido_id=pedido_encontrado.id)

        messages.error(request, "No encontramos un pedido con ese código y correo.")
        return render(
            request,
            "pedidos/consultar_pedido.html",
            {
                "codigo_inicial": codigo,
                "email_inicial": request.POST.get("email", "").strip(),
                "datos_prefill": False,
            },
        )

    return render(
        request,
        "pedidos/consultar_pedido.html",
        {
            "codigo_inicial": codigo_inicial,
            "email_inicial": email_inicial,
            "datos_prefill": datos_prefill,
        },
    )


def detalle_publico(request, pedido_id):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related("lineas"),
        pk=pedido_id,
    )

    return render(
        request,
        "pedidos/detalle_publico.html",
        {
            "pedido": pedido,
            "lineas_pedido": pedido.lineas.all(),
        },
    )


def confirmar_pedido(request):
    if request.method != "POST":
        return redirect("carrito:checkout")

    carrito = Carrito(request)
    form = PedidoClienteForm(request.POST)

    if not form.is_valid():
        logger.warning("❌ Formulario inválido: %s", form.errors)
        return render(
            request,
            "carrito/checkout.html",
            {
                "form": form,
                "carrito": carrito.carrito,
                "total": carrito.total(),
                "hoy": date.today(),
            },
        )

    if not carrito.carrito:
        return redirect("carrito:ver_carrito")

    nombre = form.cleaned_data["nombre"]
    email = form.cleaned_data["email"]
    telefono = form.cleaned_data.get("telefono", "")
    direccion = form.cleaned_data.get("direccion", "")
    fecha_evento = form.cleaned_data.get("fecha_evento", None)
    detalles = form.cleaned_data.get("detalles", "")

    logger.debug("=" * 50)
    logger.debug("DATOS DEL FORMULARIO:")
    logger.debug("Nombre: %s", nombre)
    logger.debug("Email: %s", email)
    logger.debug("Teléfono: %s", telefono)
    logger.debug("Dirección: %s", direccion)
    logger.debug("Fecha evento: %s (Tipo: %s)", fecha_evento, type(fecha_evento))
    logger.debug("Detalles_len: %s", len(detalles or ""))
    logger.debug("=" * 50)

    total = carrito.total()

    with transaction.atomic():
        pedido = Pedido.objects.create(
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
            fecha_evento=fecha_evento,
            detalles=detalles,
            total=total,
            estado=Pedido.Estado.PENDIENTE,
        )

        HistorialEstadoPedido.objects.create(
            pedido=pedido,
            estado_anterior=Pedido.Estado.PENDIENTE,
            estado_nuevo=Pedido.Estado.PENDIENTE,
            nota="Pedido creado por el cliente.",
            cambiado_por=request.user if request.user.is_authenticated else None,
        )

        logger.info(
            "PEDIDO CREADO: id=%s codigo=%s total=%s estado=%s",
            pedido.id,
            pedido.codigo_pedido,
            pedido.total,
            pedido.estado,
        )
        logger.debug("Fecha evento guardada: %s", pedido.fecha_evento)
        logger.debug("Detalles guardados: %s", pedido.detalles)

        for item in carrito.carrito.values():
            producto = Producto.objects.get(id=item["producto_id"])
            cantidad = item["cantidad"]
            precio = Decimal(item["precio"])

            LineaPedido.objects.create(
                pedido=pedido,
                producto=producto,
                nombre_producto=producto.nombre,
                precio_unitario=precio,
                cantidad=cantidad,
                subtotal=precio * cantidad,
            )

        carrito.limpiar()
        request.session.modified = True

    return redirect("pedidos:exito", pedido_id=pedido.id)


def exito(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    logger.debug(
        "PEDIDO EN VISTA EXITO: id=%s codigo=%s fecha_evento=%s detalles=%s tipo_fecha_evento=%s",
        pedido.id,
        pedido.codigo_pedido,
        pedido.fecha_evento,
        pedido.detalles,
        type(pedido.fecha_evento),
    )

    return render(request, "pedidos/exito.html", {"pedido": pedido})


def descargar_pdf(request, pedido_id):
    pedido = get_object_or_404(Pedido.objects.prefetch_related("lineas"), pk=pedido_id)

    response = HttpResponse(content_type="application/pdf")
    codigo_factura = pedido.codigo_pedido
    response["Content-Disposition"] = f'attachment; filename="factura_{codigo_factura}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 40

    brand_color = colors.HexColor("#ff8c42")
    text_dark = colors.HexColor("#5a2a00")

    pdf.setFillColor(brand_color)
    pdf.rect(0, height - 60, width, 60, fill=True)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 42, "Dulce Cayena Repostería")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(width - 220, height - 42, f"Factura: {codigo_factura}")

    y -= 90

    pdf.setFillColor(text_dark)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Datos del cliente:")
    y -= 22

    pdf.setFont("Helvetica", 11)

    info_basica = [
        f"Nombre: {pedido.nombre}",
        f"Email: {pedido.email}",
        f"Teléfono: {pedido.telefono}",
    ]

    for info in info_basica:
        pdf.drawString(45, y, f"• {info}")
        y -= 15

    y -= 5
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "Dirección de entrega:")
    y -= 14

    pdf.setFont("Helvetica", 10)
    if pedido.direccion:
        direccion_lines = []
        current_line = ""
        words = pedido.direccion.split()

        for word in words:
            if len(current_line + " " + word) <= 70:
                current_line = f"{current_line} {word}".strip()
            else:
                direccion_lines.append(current_line)
                current_line = word

        if current_line:
            direccion_lines.append(current_line)

        for line in direccion_lines:
            if y < 100:
                pdf.showPage()
                y = height - 40
                pdf.setFillColor(text_dark)
                pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y, line)
            y -= 12
    else:
        pdf.drawString(50, y, "No especificada")
        y -= 12

    y -= 8

    if pedido.fecha_evento:
        y -= 5
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(40, y, "Fecha de entrega:")
        y -= 14

        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, pedido.fecha_evento.strftime("%d/%m/%Y"))
        y -= 20

    if pedido.detalles and pedido.detalles.strip():
        y -= 10
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(40, y, "Detalles adicionales:")
        y -= 14

        pdf.setFont("Helvetica", 10)
        detalles_lines = pedido.detalles.split("\n")

        for line in detalles_lines:
            if len(line) > 70:
                sublines = []
                current_subline = ""
                words = line.split()

                for word in words:
                    if len(current_subline + " " + word) <= 70:
                        current_subline = f"{current_subline} {word}".strip()
                    else:
                        sublines.append(current_subline)
                        current_subline = word

                if current_subline:
                    sublines.append(current_subline)

                for subline in sublines:
                    if y < 100:
                        pdf.showPage()
                        y = height - 40
                        pdf.setFillColor(text_dark)
                        pdf.setFont("Helvetica", 10)
                    pdf.drawString(50, y, subline.strip())
                    y -= 12
            else:
                if y < 100:
                    pdf.showPage()
                    y = height - 40
                    pdf.setFillColor(text_dark)
                    pdf.setFont("Helvetica", 10)
                pdf.drawString(50, y, line.strip())
                y -= 12

        y -= 10

    y -= 10
    pdf.setStrokeColor(brand_color)
    pdf.line(40, y, width - 40, y)
    y -= 25

    pdf.setFillColor(text_dark)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(40, y, "Productos del pedido")
    y -= 18

    data = [["Producto", "Cant", "Precio", "Subtotal"]]
    for linea in pedido.lineas.all():
        data.append([
            linea.nombre_producto,
            str(linea.cantidad),
            f"RD$ {linea.precio_unitario:,.2f}",
            f"RD$ {linea.subtotal:,.2f}",
        ])

    table = Table(data, colWidths=[220, 45, 80, 80])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), brand_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.8, brand_color),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ])
    )

    table.wrapOn(pdf, 40, y)
    table_height = 18 * len(data)
    table.drawOn(pdf, 40, y - table_height)

    y -= table_height + 30

    y -= 10
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(width - 220, y, f"TOTAL: RD$ {pedido.total:,.2f}")
    y -= 100

    qr_code = qr.QrCodeWidget("https://wa.me/18091234567")
    size = 80
    qr_drawing = Drawing(size, size)
    qr_drawing.add(qr_code)
    renderPDF.draw(qr_drawing, pdf, width - 120, y)

    pdf.setFont("Helvetica", 9)
    pdf.drawString(width - 125, y - 12, "Confirma tu pago")
    pdf.drawString(width - 122, y - 24, "vía WhatsApp")

    pdf.setFillColor(colors.grey)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, 25, f"Gracias por preferirnos ❤️ — {codigo_factura}")

    pdf.showPage()
    pdf.save()
    return response