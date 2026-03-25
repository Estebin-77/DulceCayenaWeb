document.addEventListener("DOMContentLoaded", () => {
  const tiendaSection = document.querySelector(".tienda-section");
  const cantidadCarritoUrl = tiendaSection?.dataset.urlCantidadCarrito;

  if (!tiendaSection || !window.DulceCayenaCarrito) return;

  function renderZone(zone, cantidad, activarEventos) {
    zone.dataset.cantidad = cantidad;

    if (cantidad > 0) {
      zone.innerHTML = `
        <div class="d-flex justify-content-center align-items-center gap-2 flex-wrap">
          <button class="btn btn-outline-secondary btn-restar">-</button>
          <input type="number" min="1" class="form-control cant-input text-center"
                 value="${cantidad}" style="width:70px;" readonly>
          <button class="btn btn-outline-secondary btn-sumar">+</button>
          <button class="btn btn-danger btn-borrar">🗑</button>
        </div>
        <p class="text-muted small mt-2 mb-0">En carrito: <span class="cant-label">${cantidad}</span></p>
      `;
    } else {
      zone.innerHTML = `<button class="btn btn-warning btn-agregar">🛒 Agregar al carrito</button>`;
    }

    activarEventos(zone);
  }

  window.DulceCayenaCarrito.initPublicCart({
    sectionSelector: ".tienda-section",
    cantidadCarritoUrl,
    renderZone
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const filtrosBox = document.querySelector(".tienda-filtros-box");
  if (!filtrosBox) return;

  const form = filtrosBox.querySelector("form");
  const inputBusqueda = form?.querySelector('input[name="q"]');
  const selectOrden = form?.querySelector('select[name="orden"]');
  const catalogo = document.getElementById("catalogo-productos");

  if (!form) return;

  const enfocarCatalogo = () => {
    if (!catalogo) return;

    catalogo.setAttribute("tabindex", "-1");
    catalogo.focus({ preventScroll: true });

    requestAnimationFrame(() => {
      catalogo.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  };

  const enviarFormulario = () => {
    if (inputBusqueda) {
      inputBusqueda.value = inputBusqueda.value.trim().replace(/\s+/g, " ");
    }

    try {
      sessionStorage.setItem("tiendaScrollToCatalogo", "1");
    } catch (error) {
      // no-op
    }

    form.submit();
  };

  if (selectOrden) {
    selectOrden.addEventListener("change", () => {
      enviarFormulario();
    });
  }

  form.addEventListener("submit", () => {
    if (inputBusqueda) {
      inputBusqueda.value = inputBusqueda.value.trim().replace(/\s+/g, " ");
    }

    try {
      sessionStorage.setItem("tiendaScrollToCatalogo", "1");
    } catch (error) {
      // no-op
    }
  });

  if (inputBusqueda) {
    inputBusqueda.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        inputBusqueda.value = inputBusqueda.value.trim().replace(/\s+/g, " ");
      }
    });
  }

  try {
    const debeIrAlCatalogo = sessionStorage.getItem("tiendaScrollToCatalogo");

    if (debeIrAlCatalogo === "1") {
      sessionStorage.removeItem("tiendaScrollToCatalogo");

      setTimeout(() => {
        enfocarCatalogo();
      }, 120);
    }
  } catch (error) {
    // no-op
  }
});