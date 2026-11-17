# Recurso: sesiones (vive en Redis)
# Cada sesion = un visitante navegando en un sitio durante un rato.
# Estructura:
#   sesion:{id}          -> hash con los datos de la sesion
#   sitio:{id}:activas   -> sorted set con la ultima actividad (score = timestamp)
# IMPORTANTE: no se usa EXPIRE/TTL porque sino Redis borraria la sesion
# fisicamente y romperia la regla de borrado logico.
import time, uuid
from flask import Blueprint, request, jsonify
from db import r

sesiones_bp = Blueprint("sesiones", __name__)


def _sesion_a_dict(datos):
    """Convierte el hash de Redis a un diccionario normal."""
    if not datos:
        return None
    return {
        "id": datos.get("id"),
        "sitio_id": int(datos["sitio_id"]) if datos.get("sitio_id") else None,
        "visitante_id": datos.get("visitante_id"),
        "inicio": float(datos["inicio"]) if datos.get("inicio") else None,
        "ultima_actividad": float(datos["ultima_actividad"]) if datos.get("ultima_actividad") else None,
        "paginas_vistas": int(datos.get("paginas_vistas", 0)),
        "estado": datos.get("estado"),
        "eliminado": datos.get("eliminado") == "1",
    }


def sesiones_registradas(sitio_id=None):
    for clave in r.scan_iter("sesion:*"):
        datos = r.hgetall(clave)
        if not datos or datos.get("eliminado") == "1":
            continue
        if sitio_id and datos.get("sitio_id") != sitio_id:
            continue
        yield _sesion_a_dict(datos)


@sesiones_bp.get("/api/sesiones")
def listar_sesiones():
    """Lista todas las sesiones no borradas. ?sitio_id=1 filtra por sitio."""
    return jsonify(list(sesiones_registradas(request.args.get("sitio_id"))))


@sesiones_bp.get("/api/sesiones/<id>")
def ver_sesion(id):
    datos = r.hgetall(f"sesion:{id}")
    if not datos or datos.get("eliminado") == "1":
        return jsonify({"error": "Sesion no encontrada"}), 404
    return jsonify(_sesion_a_dict(datos))


@sesiones_bp.post("/api/sesiones")
def crear_sesion():
    datos = request.get_json() or {}
    if not datos.get("sitio_id") or not datos.get("visitante_id"):
        return jsonify({"error": "sitio_id y visitante_id son obligatorios"}), 400
    sesion_id = str(uuid.uuid4())
    ahora = time.time()
    r.hset(f"sesion:{sesion_id}", mapping={
        "id": sesion_id,
        "sitio_id": datos["sitio_id"],
        "visitante_id": datos["visitante_id"],
        "inicio": ahora,
        "ultima_actividad": ahora,
        "paginas_vistas": 1,
        "estado": "activa",
        "eliminado": 0,
    })
    # la metemos al sorted set de sesiones activas del sitio
    r.zadd(f"sitio:{datos['sitio_id']}:activas", {sesion_id: ahora})
    return jsonify({"mensaje": "Sesion creada", "id": sesion_id}), 201


@sesiones_bp.patch("/api/sesiones/<id>")
def actualizar_sesion(id):
    """Cada vez que el visitante hace algo, se renueva ultima_actividad."""
    datos = r.hgetall(f"sesion:{id}")
    if not datos or datos.get("eliminado") == "1":
        return jsonify({"error": "Sesion no encontrada"}), 404
    cambios = request.get_json() or {}
    ahora = time.time()
    cambios["ultima_actividad"] = ahora
    if cambios.get("suma_pagina"):
        cambios["paginas_vistas"] = int(datos.get("paginas_vistas", 0)) + 1
        cambios.pop("suma_pagina")
    r.hset(f"sesion:{id}", mapping={k: v for k, v in cambios.items()})
    r.zadd(f"sitio:{datos['sitio_id']}:activas", {id: ahora})
    return jsonify({"mensaje": "Sesion actualizada"})


@sesiones_bp.delete("/api/sesiones/<id>")
def borrar_sesion(id):
    """Borrado LOGICO: NO usamos DEL, solo marcamos eliminado=1."""
    datos = r.hgetall(f"sesion:{id}")
    if not datos or datos.get("eliminado") == "1":
        return jsonify({"error": "Sesion no encontrada"}), 404
    r.hset(f"sesion:{id}", mapping={
        "eliminado": 1,
        "estado": "cerrada",
        "eliminado_en": time.time(),
    })
    # la sacamos del sorted set para que no cuente como activa
    r.zrem(f"sitio:{datos['sitio_id']}:activas", id)
    return jsonify({"mensaje": "Sesion marcada como borrada"})
