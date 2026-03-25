document.addEventListener("DOMContentLoaded", () => {
  const detalleSection = document.querySelector(".detalle-section");
  const cantidadCarritoUrl = detalleSection?.dataset.urlCantidadCarrito;

  if (!detalleSection || !window.DulceCayenaCarrito) return;

  function actualizarEstadoProductoPrincipal(productId, cantidad) {
    const estado = document.querySelector(
      `.detalle-carrito-estado[data-producto-principal-id="${productId}"]`
    );

    if (!estado) return;

    if (cantidad > 0) {
      estado.textContent = cantidad === 1 ? "1 agregado" : `${cantidad} agregados`;
    } else {
      estado.textContent = "Aún no agregado";
    }
  }

  function renderZone(zone, cantidad, activarEventos) {
    zone.dataset.cantidad = cantidad;

    if (cantidad > 0) {
      zone.innerHTML = `
        <div class="d-flex align-items-center gap-2 flex-wrap justify-content-center justify-content-lg-start">
          <button class="btn btn-outline-secondary btn-restar">-</button>
          <input
            type="number"
            min="1"
            class="form-control cant-input text-center"
            value="${cantidad}"
            style="width:90px;"
            readonly
          >
          <button class="btn btn-outline-secondary btn-sumar">+</button>
          <button class="btn btn-danger btn-borrar">🗑</button>
        </div>
        <p class="text-muted small mt-2 mb-0">
          En carrito: <span class="cant-label">${cantidad}</span>
        </p>
      `;
    } else {
      const isMainDetailZone = zone.classList.contains("mt-4");

      zone.innerHTML = `
        <button class="btn btn-warning btn-agregar ${isMainDetailZone ? "btn-detalle-agregar px-4 py-3" : ""}">
          🛒 Agregar al carrito
        </button>
      `;
    }

    activarEventos(zone);
  }

  window.DulceCayenaCarrito.initPublicCart({
    sectionSelector: ".detalle-section",
    cantidadCarritoUrl,
    renderZone,
    afterSync: actualizarEstadoProductoPrincipal
  });
});