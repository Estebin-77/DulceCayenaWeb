from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

from .forms import PedidoClienteForm
from .models import Pedido, LineaPedido
from carrito.carrito import Carrito
from tienda.models import Producto
import logging 

logger = logging.getLogger(__name__)


def confirmar_pedido(request):
    if request.method != "POST":
        return redirect('carrito:checkout')

    form = PedidoClienteForm(request.POST)
    if not form.is_valid():
        logger.warning("❌ Formulario inválido: %s", form.errors)  # DEBUG
        return render(request, "carrito/checkout.html", {"form": form})

    carrito = Carrito(request)
    if not carrito.carrito:
        return redirect('carrito:ver_carrito')

    nombre = form.cleaned_data['nombre']
    email = form.cleaned_data['email']
    telefono = form.cleaned_data.get('telefono', '')
    direccion = form.cleaned_data.get('direccion', '')
    fecha_evento = form.cleaned_data.get('fecha_evento', None)
    detalles = form.cleaned_data.get('detalles', '')

    # DEBUG: Verificar los datos del formulario
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

    # Crear el pedido (atómico)
    with transaction.atomic():
        pedido = Pedido.objects.create(
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
            fecha_evento=fecha_evento,
            detalles=detalles,
            total=total,
            estado='pendiente',
        )

        # DEBUG: Verificar el pedido creado
        logger.info("PEDIDO CREADO: id=%s total=%s estado=%s", pedido.id, pedido.total, pedido.estado)
        logger.debug("Fecha evento guardada: %s", pedido.fecha_evento)
        logger.debug("Detalles guardados: %s", pedido.detalles)

        # Crear líneas de pedido
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


    return redirect('pedidos:exito', pedido_id=pedido.id)


def exito(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    
    # DEBUG: Verificar qué contiene el pedido en la base de datos
    logger.debug("PEDIDO EN VISTA EXITO: id=%s fecha_evento=%s detalles=%s tipo_fecha_evento=%s",
                pedido.id, pedido.fecha_evento, pedido.detalles, type(pedido.fecha_evento))

    
    return render(request, 'pedidos/exito.html', {"pedido": pedido})


def descargar_pdf(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    response = HttpResponse(content_type='application/pdf')

    ano = date.today().year
    codigo_factura = f"DC-{pedido.id:04d}-{ano}"


    response['Content-Disposition'] = f'attachment; filename="factura_{codigo_factura}.pdf"'


    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 40

    brand_color = colors.HexColor("#ff8c42")
    text_dark = colors.HexColor("#5a2a00")

    # ✅ Encabezado
    pdf.setFillColor(brand_color)
    pdf.rect(0, height - 60, width, 60, fill=True)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 42, "Dulce Cayena Repostería")


    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(width - 200, height - 42, f"Factura: {codigo_factura}")

    y -= 90

    # ✅ Datos Cliente
    pdf.setFillColor(text_dark)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Datos del cliente:")
    y -= 22

    pdf.setFont("Helvetica", 11)
    
    # ✅ Información básica del cliente
    info_basica = [
        f"Nombre: {pedido.nombre}",
        f"Email: {pedido.email}",
        f"Teléfono: {pedido.telefono}",
    ]

    for info in info_basica:
        pdf.drawString(45, y, f"• {info}")
        y -= 15

    # ✅ DIRECCIÓN CON MANEJO DE TEXTO MULTILÍNEA
    y -= 5  # Espacio adicional antes de la dirección
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "📍 Dirección de entrega:")
    y -= 14
    
    pdf.setFont("Helvetica", 10)
    if pedido.direccion:
        # Dividir la dirección en líneas de máximo 70 caracteres
        direccion_lines = []
        current_line = ""
        words = pedido.direccion.split()
        
        for word in words:
            if len(current_line + " " + word) <= 70:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                direccion_lines.append(current_line)
                current_line = word
        
        if current_line:
            direccion_lines.append(current_line)
        
        # Dibujar cada línea de la dirección
        for line in direccion_lines:
            if y < 100:  # Si queda poco espacio, crear nueva página
                pdf.showPage()
                y = height - 40
                pdf.setFillColor(text_dark)
                pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y, line)
            y -= 12
    else:
        pdf.drawString(50, y, "No especificada")
        y -= 12
    
    y -= 8  # Espacio después de la dirección

    # ✅ Fecha del evento
    if pedido.fecha_evento:
        y -= 5
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(40, y, "📅 Fecha de entrega:")
        y -= 14
        
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, pedido.fecha_evento.strftime('%d/%m/%Y'))
        y -= 20

    # ✅ Detalles adicionales
    if pedido.detalles and pedido.detalles.strip():
        y -= 10
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(40, y, "📝 Detalles adicionales:")
        y -= 14
        
        pdf.setFont("Helvetica", 10)
        detalles_lines = pedido.detalles.split('\n')
        for line in detalles_lines:
            # También dividir líneas muy largas en detalles
            if len(line) > 70:
                sublines = []
                current_subline = ""
                words = line.split()
                
                for word in words:
                    if len(current_subline + " " + word) <= 70:
                        if current_subline:
                            current_subline += " " + word
                        else:
                            current_subline = word
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

    # Línea separadora
    y -= 10
    pdf.setStrokeColor(brand_color)
    pdf.line(40, y, width - 40, y)
    y -= 25

    # ✅ Título tabla
    pdf.setFillColor(text_dark)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(40, y, "Productos del pedido")
    y -= 18

    # ✅ Tabla de productos CON FORMATO DE MONEDA
    data = [["Producto", "Cant", "Precio", "Subtotal"]]
    for linea in pedido.lineas.all():
        data.append([
            linea.nombre_producto,
            str(linea.cantidad),
            f"RD$ {linea.precio_unitario:,.2f}",
            f"RD$ {linea.subtotal:,.2f}",
        ])

    table = Table(data, colWidths=[220, 45, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.8, brand_color),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    table.wrapOn(pdf, 40, y)
    table_height = 18 * len(data)
    table.drawOn(pdf, 40, y - table_height)

    y -= table_height + 30

    # ✅ Total resaltado CON FORMATO DE MONEDA
    y -= 10
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(width - 200, y, f"TOTAL: RD$ {pedido.total:,.2f}")
    y -= 100

    # ✅ QR con texto
    qr_code = qr.QrCodeWidget("https://wa.me/18091234567")
    size = 80
    qr_drawing = Drawing(size, size)
    qr_drawing.add(qr_code)
    renderPDF.draw(qr_drawing, pdf, width - 120, y)

    pdf.setFont("Helvetica", 9)
    pdf.drawString(width - 125, y - 12, "Confirma tu pago")
    pdf.drawString(width - 122, y - 24, "vía WhatsApp")

    # ✅ Pie de página
    pdf.setFillColor(colors.grey)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, 25, "Gracias por preferirnos ❤️ — Dulce Cayena Web")

    pdf.showPage()
    pdf.save()
    return response