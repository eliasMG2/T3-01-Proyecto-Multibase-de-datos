// Tracker: el "espia" que vive en la pagina y manda lo que hace el visitante a la API.
// Se ejecuta en cada pagina y hace 3 cosas:
//   1. Si no hay sesion abierta, crea una (POST /api/sesiones)
//   2. Registra la visita a la pagina (POST /api/eventos)   <-- este lo hace Elias
//   3. Registra cada clic en un boton    (POST /api/eventos)   <-- este lo hace Elias
const API = "http://localhost:5000";
const SITIO_ID = 1;   // debes crear el sitio con id=1 antes de probar

// visitante_id: lo guardamos en el navegador para que persista entre paginas
let visitanteId = localStorage.getItem("visitante_id");
if (!visitanteId) {
  visitanteId = "v-" + Math.random().toString(36).slice(2, 10);
  localStorage.setItem("visitante_id", visitanteId);
}

// sesion_id: dura mientras la pestana no se cierre (sessionStorage)
async function asegurarSesion() {
  let sid = sessionStorage.getItem("sesion_id");
  if (sid) return sid;
  const resp = await fetch(API + "/api/sesiones", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({sitio_id: SITIO_ID, visitante_id: visitanteId})
  });
  const data = await resp.json();
  sid = data.id;
  sessionStorage.setItem("sesion_id", sid);
  return sid;
}

function log(texto) {
  const div = document.getElementById("log");
  if (div) div.innerHTML += texto + "<br>";
  console.log(texto);
}

// Manda evento al API (visita o clic). El endpoint /api/eventos lo hace Elias.
async function mandarEvento(tipo, extra = {}) {
  const sesionId = await asegurarSesion();
  const evento = {
    sitio_id: SITIO_ID,
    sesion_id: sesionId,
    visitante_id: visitanteId,
    tipo: tipo,
    ruta: window.location.pathname.split("/").pop() || "index",
    ...extra
  };
  try {
    await fetch(API + "/api/eventos", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(evento)
    });
    log("[" + new Date().toLocaleTimeString() + "] " + tipo + " -> " + JSON.stringify(evento));
  } catch (e) {
    log("[error] no se pudo mandar (¿Flask corriendo? ¿Elias ya hizo /api/eventos?): " + e);
  }
  // Actualizamos la sesion: renueva ultima_actividad
  fetch(API + "/api/sesiones/" + sesionId, {
    method: "PATCH",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({suma_pagina: true})
  });
}

// === cuando la pagina carga: evento "visita" ===
window.addEventListener("load", () => mandarEvento("visita"));

// === cada clic en un boton o un link: evento "clic" ===
document.addEventListener("click", (e) => {
  const el = e.target;
  if (el.tagName === "BUTTON" || el.tagName === "A") {
    mandarEvento("clic", {datos: {texto: el.innerText, selector: el.id || el.className || el.tagName}});
  }
});
