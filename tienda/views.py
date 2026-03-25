from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Categoria, Producto


def aplicar_cantidades_carrito(productos, carrito):
    for producto in productos:
        producto.cant_en_carrito = carrito.get(str(producto.id), {}).get("cantidad", 0)
    return productos


def construir_textos_tienda(
    categoria_actual,
    total_productos,
    total_categorias,
    busqueda_actual="",
):
    if categoria_actual and busqueda_actual:
        hero_titulo = f'Resultados para "{busqueda_actual}" en {categoria_actual.nombre}'
        hero_descripcion = (
            f"Explora nuestra selección de {categoria_actual.nombre.lower()} que coincide "
            "con tu búsqueda, elaborada con dedicación, detalle y el estilo artesanal "
            "de Dulce Cayena."
        )
        bloque_resumen = (
            f"{total_productos} resultado{'s' if total_productos != 1 else ''} "
            f'para “{busqueda_actual}” en esta categoría.'
        )
        etiqueta_resultados = (
            f"{total_productos} resultado{'s' if total_productos != 1 else ''}"
        )

    elif categoria_actual:
        hero_titulo = categoria_actual.nombre
        hero_descripcion = (
            f"Explora nuestra selección de {categoria_actual.nombre.lower()}, "
            "elaborada con dedicación, detalle y el estilo artesanal de Dulce Cayena."
        )
        bloque_resumen = (
            f"{total_productos} producto{'s' if total_productos != 1 else ''} "
            "disponible" + ("s" if total_productos != 1 else "")
            + " en esta categoría."
        )
        etiqueta_resultados = (
            f"{total_productos} producto{'s' if total_productos != 1 else ''}"
        )

    elif busqueda_actual:
        hero_titulo = f'Resultados para "{busqueda_actual}"'
        hero_descripcion = (
            "Descubre los productos artesanales de Dulce Cayena que coinciden con tu "
            "búsqueda y encuentra más rápido lo que deseas."
        )
        bloque_resumen = (
            f"{total_productos} resultado{'s' if total_productos != 1 else ''} "
            f'para “{busqueda_actual}” en {total_categorias} categor'
            f"{'ías' if total_categorias != 1 else 'ía'}."
        )
        etiqueta_resultados = (
            f"{total_productos} resultado{'s' if total_productos != 1 else ''}"
        )

    else:
        hero_titulo = "Nuestra tienda"
        hero_descripcion = (
            "Descubre postres y productos artesanales hechos con dedicación, "
            "pensados para momentos especiales, regalos dulces y antojos inolvidables."
        )
        bloque_resumen = (
            f"{total_productos} producto{'s' if total_productos != 1 else ''} disponible"
            f"{'s' if total_productos != 1 else ''} en {total_categorias} categor"
            f"{'ías' if total_categorias != 1 else 'ía'}."
        )
        etiqueta_resultados = (
            f"{total_productos} producto{'s' if total_productos != 1 else ''}"
        )

    return {
        "hero_titulo": hero_titulo,
        "hero_descripcion": hero_descripcion,
        "bloque_resumen": bloque_resumen,
        "etiqueta_resultados": etiqueta_resultados,
    }


def construir_paginas_visibles(page_obj):
    total_paginas = page_obj.paginator.num_pages
    pagina_actual = page_obj.number

    if total_paginas <= 7:
        return list(range(1, total_paginas + 1))

    paginas = {1, total_paginas}

    for numero in range(pagina_actual - 1, pagina_actual + 2):
        if 1 <= numero <= total_paginas:
            paginas.add(numero)

    if pagina_actual <= 3:
        paginas.update({2, 3, 4})
    elif pagina_actual >= total_paginas - 2:
        paginas.update({total_paginas - 3, total_paginas - 2, total_paginas - 1})

    paginas_ordenadas = sorted(numero for numero in paginas if 1 <= numero <= total_paginas)

    paginas_visibles = []
    anterior = None

    for numero in paginas_ordenadas:
        if anterior is not None and numero - anterior > 1:
            paginas_visibles.append(None)
        paginas_visibles.append(numero)
        anterior = numero

    return paginas_visibles


def tienda(request, categoria_slug=None):
    categoria_actual = None
    busqueda_actual = request.GET.get("q", "").strip()
    orden_actual = request.GET.get("orden", "relevancia").strip()

    if categoria_slug:
        categoria_actual = get_object_or_404(
            Categoria,
            slug=categoria_slug,
            activa=True,
        )

    categorias_qs = (
        Categoria.objects.filter(activa=True)
        .annotate(
            productos_disponibles=Count(
                "productos",
                filter=Q(productos__disponible=True)
            )
        )
        .order_by("nombre")
    )

    if categoria_actual:
        categorias_qs = categorias_qs.filter(
            Q(productos_disponibles__gt=0) | Q(id=categoria_actual.id)
        )
    else:
        categorias_qs = categorias_qs.filter(productos_disponibles__gt=0)

    productos_qs = (
        Producto.objects.filter(disponible=True)
        .select_related("categoria")
    )

    if categoria_actual:
        productos_qs = productos_qs.filter(categoria=categoria_actual)

    if busqueda_actual:
        productos_qs = productos_qs.filter(
            Q(nombre__icontains=busqueda_actual)
            | Q(descripcion__icontains=busqueda_actual)
            | Q(categoria__nombre__icontains=busqueda_actual)
        )

    opciones_orden = {
        "relevancia": ("-destacado", "-creado", "nombre"),
        "nombre_asc": ("nombre",),
        "nombre_desc": ("-nombre",),
        "precio_asc": ("precio", "nombre"),
        "precio_desc": ("-precio", "nombre"),
        "recientes": ("-creado", "nombre"),
    }

    if orden_actual not in opciones_orden:
        orden_actual = "relevancia"

    productos_qs = productos_qs.order_by(*opciones_orden[orden_actual])

    destacados_qs = Producto.objects.none()
    if not categoria_actual and not busqueda_actual:
        destacados_qs = (
            Producto.objects.filter(disponible=True, destacado=True)
            .select_related("categoria")
            .order_by("-creado", "nombre")[:4]
        )

    carrito = request.session.get("carrito", {})

    categorias = list(categorias_qs)
    destacados = list(destacados_qs)
    aplicar_cantidades_carrito(destacados, carrito)

    paginator = Paginator(productos_qs, 9)
    numero_pagina = request.GET.get("page")
    page_obj = paginator.get_page(numero_pagina)
    productos = list(page_obj.object_list)
    aplicar_cantidades_carrito(productos, carrito)

    total_productos = paginator.count
    total_categorias = len(categorias)

    filtros_activos = 0
    if categoria_actual:
        filtros_activos += 1
    if busqueda_actual:
        filtros_activos += 1
    if orden_actual != "relevancia":
        filtros_activos += 1

    textos = construir_textos_tienda(
        categoria_actual=categoria_actual,
        total_productos=total_productos,
        total_categorias=total_categorias,
        busqueda_actual=busqueda_actual,
    )

    context = {
        "productos": productos,
        "categorias": categorias,
        "categoria_actual": categoria_actual,
        "destacados": destacados,
        "total_productos": total_productos,
        "total_categorias": total_categorias,
        "busqueda_actual": busqueda_actual,
        "orden_actual": orden_actual,
        "filtros_activos": filtros_activos,
        "opciones_orden": [
            ("relevancia", "Relevancia"),
            ("nombre_asc", "Nombre: A-Z"),
            ("nombre_desc", "Nombre: Z-A"),
            ("precio_asc", "Precio: menor a mayor"),
            ("precio_desc", "Precio: mayor a menor"),
            ("recientes", "Más recientes"),
        ],
        "page_obj": page_obj,
        "is_paginated": page_obj.paginator.num_pages > 1,
        "paginas_visibles": construir_paginas_visibles(page_obj),
        **textos,
    }

    return render(request, "tienda/tienda.html", context)


def detalle_producto(request, slug):
    producto = get_object_or_404(
        Producto.objects.select_related("categoria"),
        slug=slug,
        disponible=True,
    )

    carrito = request.session.get("carrito", {})
    producto.cant_en_carrito = carrito.get(str(producto.id), {}).get("cantidad", 0)

    relacionados = list(
        Producto.objects.filter(
            disponible=True,
            categoria=producto.categoria,
        )
        .exclude(id=producto.id)
        .select_related("categoria")
        .order_by("-destacado", "-creado", "nombre")[:4]
    )

    aplicar_cantidades_carrito(relacionados, carrito)

    return render(request, "tienda/detalle_producto.html", {
        "producto": producto,
        "relacionados": relacionados,
    })