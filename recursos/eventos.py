# Recurso: eventos (vive en MongoDB)
# Un evento = algo que un visitante hizo (visita a una pagina, un clic, un scroll).
# Cada evento tiene atributos distintos segun el tipo, por eso vive en Mongo y no en SQL.
#
# ⚠️ Para Elias: este es el recurso mas distinto. En MongoDB no se usan SQL ni cursor,
# se usan metodos como insert_one, find, update_one y delete_one(con $set:eliminado).
# OJO IMPORTANTE: el PATCH SOLO deja cambiar 'etiquetas' y 'revisado'. Un evento es
# un hecho ocurrido: no se puede "corregir" que alguien visito la pagina, solo
# etiquetarlo o marcarlo como revisado.
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from db import mongo

eventos_bp = Blueprint("eventos", __name__)
col = mongo["eventos"]  # la coleccion de MongoDB donde vivimos

# Solo estos dos campos se pueden editar despues de registrado el evento
CAMPOS_EDITABLES = ["etiquetas", "revisado"]


def _serializar(doc):
    """MongoDB usa ObjectId, que no es JSON. Lo convertimos a texto."""
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    if "fecha" in doc and hasattr(doc["fecha"], "isoformat"):
        doc["fecha"] = doc["fecha"].isoformat()
    return doc


@eventos_bp.get("/api/eventos")
def listar_eventos():
    # Filtra eventos no eliminados. ?sitio_id=1 filtra por sitio.
    filtro = {"eliminado": {"$ne": True}}
    sitio_id = request.args.get("sitio_id")
    if sitio_id:
        filtro["sitio_id"] = int(sitio_id)
    datos = [_serializar(d) for d in col.find(filtro).limit(100)]
    return jsonify(datos)


@eventos_bp.get("/api/eventos/<id>")
def ver_evento(id):
    try:
        doc = col.find_one({"_id": ObjectId(id), "eliminado": {"$ne": True}})
    except Exception:
        return jsonify({"error": "id invalido"}), 400
    if doc is None:
        return jsonify({"error": "Evento no encontrado"}), 404
    return jsonify(_serializar(doc))


@eventos_bp.post("/api/eventos")
def crear_evento():
    datos = request.get_json() or {}
    if not datos.get("tipo") or not datos.get("sitio_id"):
        return jsonify({"error": "tipo y sitio_id son obligatorios"}), 400
    # Agregamos campos de control
    datos["fecha"] = datetime.utcnow()
    datos["eliminado"] = False
    datos.setdefault("etiquetas", [])
    datos.setdefault("revisado", False)
    resultado = col.insert_one(datos)
    return jsonify({"mensaje": "Evento registrado", "id": str(resultado.inserted_id)}), 201


@eventos_bp.patch("/api/eventos/<id>")
def editar_evento(id):
    datos = request.get_json() or {}
    cambios = {k: v for k, v in datos.items() if k in CAMPOS_EDITABLES}
    if not cambios:
        return jsonify({"error": f"Solo se pueden editar: {CAMPOS_EDITABLES}"}), 400
    try:
        r = col.update_one(
            {"_id": ObjectId(id), "eliminado": {"$ne": True}},
            {"$set": cambios}
        )
    except Exception:
        return jsonify({"error": "id invalido"}), 400
    if r.matched_count == 0:
        return jsonify({"error": "Evento no encontrado"}), 404
    return jsonify({"mensaje": "Evento actualizado"})


@eventos_bp.delete("/api/eventos/<id>")
def borrar_evento(id):
    # Borrado logico: NO usamos delete_one, solo marcamos eliminado=True
    try:
        r = col.update_one(
            {"_id": ObjectId(id), "eliminado": {"$ne": True}},
            {"$set": {"eliminado": True, "eliminado_en": datetime.utcnow()}}
        )
    except Exception:
        return jsonify({"error": "id invalido"}), 400
    if r.matched_count == 0:
        return jsonify({"error": "Evento no encontrado"}), 404
    return jsonify({"mensaje": "Evento marcado como borrado"})
