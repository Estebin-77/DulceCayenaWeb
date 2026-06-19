# Checklist QA - Dulce Cayena Web

Usa esta lista despues de desplegar cambios o levantar una base de datos nueva.

## Preparar datos demo

```bash
python manage.py migrate
python manage.py cargar_productos_demo
python manage.py cargar_servicios_demo
```

Los comandos son idempotentes: puedes ejecutarlos mas de una vez sin duplicar datos.

## Tienda y carrito

- Abrir `/tienda/` y confirmar que aparecen productos y categorias.
- Agregar un producto al carrito.
- Sumar cantidad desde la tienda.
- Restar cantidad desde la tienda.
- Eliminar el producto desde la tienda.
- Abrir `/carrito/` y confirmar que el carrito muestra productos.
- Vaciar el carrito y confirmar que aparece el estado vacio.
- Confirmar que las acciones del carrito usan POST y CSRF.

## Pedido completo

- Agregar un producto al carrito.
- Abrir `/carrito/checkout/`.
- Abrir el modal de finalizar pedido.
- Completar nombre, email, telefono, direccion, fecha de entrega y detalles.
- Confirmar el pedido.
- Guardar el codigo del pedido mostrado en la pantalla de exito.
- Abrir el detalle publico desde el boton de consulta.
- Descargar el PDF y confirmar que responde correctamente.
- Abrir `/pedidos/consultar/`.
- Consultar el pedido con codigo y email.
- Confirmar que redirige al detalle publico del pedido.

## Servicios

- Abrir `/servicios/` y confirmar que se muestran servicios activos.
- Entrar al detalle de un servicio.
- Enviar una solicitud con datos de prueba.
- Confirmar que redirige a la pagina de gracias.
- Revisar en admin que la solicitud quedo vinculada al servicio correcto.

## Contacto y blog

- Abrir `/contacto/`.
- Enviar un mensaje de prueba si no hay riesgo de notificaciones reales.
- Abrir `/blog/`.
- Abrir un post si existen publicaciones.

## Admin

- Entrar a `/admin/`.
- Confirmar que se listan productos, servicios, pedidos y solicitudes.
- Revisar un pedido reciente y sus lineas.
- Cambiar estado de un pedido de prueba siguiendo los estados permitidos.

## Pruebas locales

```bash
python manage.py check
python manage.py test
```
