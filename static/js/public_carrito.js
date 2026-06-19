window.DulceCayenaCarrito = (() => {
  const $$ = (selector, root = document) => root.querySelectorAll(selector);

  function showToast(msg) {
    const t = document.createElement("div");
    t.className = "toast-msg";
    t.innerText = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
  }

  function getCsrfToken() {
    return window.DulceCayena?.getCsrfToken?.() || "";
  }

  async function hit(url) {
    const res = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCsrfToken()
      }
    });

    if (!res.ok) {
      throw new Error(`Error al actualizar carrito: ${res.status}`);
    }

    window.dispatchEvent(new Event("carrito-actualizado"));
    return res;
  }

  async function refreshCounter(cantidadCarritoUrl) {
    if (!cantidadCarritoUrl) return;

    try {
      const res = await fetch(cantidadCarritoUrl);
      const data = await res.json();
      const badge = document.getElementById("contadorCarrito");

      if (!badge) return;

      badge.style.display = data.cantidad > 0 ? "inline-block" : "none";
      badge.textContent = data.cantidad;
    } catch (e) {
      console.error("Error contador:", e);
    }
  }

  function getZonesByProductId(productId) {
    return Array.from($$(`.carrito-acciones[data-id="${productId}"]`));
  }

  function initPublicCart(config) {
    const {
      sectionSelector,
      cantidadCarritoUrl,
      renderZone,
      afterSync
    } = config;

    const root = document.querySelector(sectionSelector);
    if (!root) return;

    function syncProductZones(productId, cantidad) {
      const zones = getZonesByProductId(productId);

      zones.forEach((zone) => renderZone(zone, cantidad, activarEventos));

      if (typeof afterSync === "function") {
        afterSync(productId, cantidad);
      }

      refreshCounter(cantidadCarritoUrl);
    }

    function activarEventos(zone) {
      const productId = zone.dataset.id;
      const urlAdd = zone.dataset.urlAdd;
      const urlSub = zone.dataset.urlSub;
      const urlDel = zone.dataset.urlDel;

      const btnAgregar = zone.querySelector(".btn-agregar");
      const btnSum = zone.querySelector(".btn-sumar");
      const btnRes = zone.querySelector(".btn-restar");
      const btnDel = zone.querySelector(".btn-borrar");

      if (btnAgregar) {
        btnAgregar.onclick = async (e) => {
          e.preventDefault();
          e.stopPropagation();
          await hit(urlAdd);
          syncProductZones(productId, 1);
          showToast("✅ Producto añadido al carrito");
        };
      }

      if (btnSum) {
        btnSum.onclick = async () => {
          const actual = Number(zone.dataset.cantidad || 0);
          const nueva = actual + 1;
          await hit(urlAdd);
          syncProductZones(productId, nueva);
        };
      }

      if (btnRes) {
        btnRes.onclick = async () => {
          const actual = Number(zone.dataset.cantidad || 0);

          if (actual <= 1) {
            await hit(urlDel);
            syncProductZones(productId, 0);
          } else {
            const nueva = actual - 1;
            await hit(urlSub);
            syncProductZones(productId, nueva);
          }
        };
      }

      if (btnDel) {
        btnDel.onclick = async () => {
          await hit(urlDel);
          syncProductZones(productId, 0);
        };
      }
    }

    const seen = new Set();

    $$(".carrito-acciones", root).forEach((zone) => {
      const productId = zone.dataset.id;

      if (seen.has(productId)) return;
      seen.add(productId);

      const cantidad = Number(zone.dataset.cantidad || 0);
      syncProductZones(productId, cantidad);
    });
  }

  return {
    initPublicCart,
    refreshCounter
  };
})();
