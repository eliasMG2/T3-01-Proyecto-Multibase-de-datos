const API = "/api";
let visitanteId = localStorage.getItem("visitante_id");
if (!visitanteId) {
  visitanteId = "v-" + Math.random().toString(36).slice(2);
  localStorage.setItem("visitante_id", visitanteId);
}

async function solicitar(ruta, metodo = "GET", datos) {
  const opciones = {method: metodo};
  if (datos !== undefined) {
    opciones.headers = {"Content-Type": "application/json"};
    opciones.body = JSON.stringify(datos);
  }
  const respuesta = await fetch(API + ruta, opciones);
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    throw new Error(detalle.error || `${metodo} ${ruta}: HTTP ${respuesta.status}`);
  }
  return respuesta.json();
}

async function asegurarSesion() {
  const sitios = await solicitar("/sitios");
  const sitio = sitios.find(({dominio}) => dominio === "mitienda.com") || sitios[0];
  if (!sitio) {
    throw new Error("Crea un sitio de prueba con seed.py y recarga la página.");
  }

  const sitioId = sitio.id;
  const clave = `sesion_id:${sitioId}`;
  const idGuardado = sessionStorage.getItem(clave);
  if (idGuardado) {
    const respuesta = await fetch(`${API}/sesiones/${idGuardado}`);
    if (respuesta.ok) return {sitioId, id: idGuardado, nueva: false};
    if (respuesta.status !== 404) {
      throw new Error(`No se pudo recuperar la sesión: HTTP ${respuesta.status}`);
    }
  }

  const {id} = await solicitar("/sesiones", "POST", {
    sitio_id: sitioId,
    visitante_id: visitanteId
  });
  sessionStorage.setItem(clave, id);
  return {sitioId, id, nueva: true};
}

function log(texto) {
  const registro = document.getElementById("log");
  if (registro) {
    const linea = document.createElement("div");
    linea.textContent = texto;
    registro.append(linea);
  }
}

async function registrarEvento(tipo, datos) {
  try {
    const sesion = await sesionActual;
    const evento = {
      sitio_id: sesion.sitioId,
      sesion_id: sesion.id,
      visitante_id: visitanteId,
      tipo,
      ruta: window.location.pathname.split("/").pop(),
      datos
    };
    const {id} = await solicitar("/eventos", "POST", evento);
    log(`${tipo} registrado: ${id}`);

    // Redis cuenta la primera página al crear la sesión.
    if (tipo === "clic" || !sesion.nueva) {
      const cambios = tipo === "visita" ? {suma_pagina: true} : {};
      await solicitar(`/sesiones/${sesion.id}`, "PATCH", cambios);
    }
  } catch (error) {
    log(error.message);
  }
}

const sesionActual = asegurarSesion();
const visitaInicial = registrarEvento("visita");

document.addEventListener("click", async (evento) => {
  const elemento = evento.target.closest("button, a");
  if (!elemento || elemento.hasAttribute("data-ignorar-analiticas")) return;

  const enlaceInterno = elemento.tagName === "A" && elemento.origin === location.origin;
  const navegar = enlaceInterno && !evento.defaultPrevented && !elemento.target &&
    !evento.ctrlKey && !evento.metaKey && !evento.shiftKey && !evento.altKey;
  if (navegar) evento.preventDefault();

  await visitaInicial;
  await registrarEvento("clic", {
    texto: elemento.innerText,
    selector: elemento.id || elemento.className || elemento.tagName
  });
  if (navegar) location.assign(elemento.href);
});
