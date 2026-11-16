# Recurso: objetivos (vive en MySQL)
# Un objetivo = algo que queremos medir en el sitio (ej: "llegar a /gracias", "dar clic en Comprar").
#
# ⚠️ Para Elias: mismo molde que usuarios. Revisa, pruebalo y si te late lo dejas asi.
from flask import Blueprint, request, jsonify
from db import conectar_mysql

objetivos_bp = Blueprint("objetivos", __name__)

CAMPOS_EDITABLES = ["nombre", "tipo", "valor"]


@objetivos_bp.get("/api/objetivos")
def listar_objetivos():
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM objetivos WHERE eliminado_en IS NULL")
        datos = cur.fetchall()
    con.close()
    return jsonify(datos)


@objetivos_bp.get("/api/objetivos/<int:id>")
def ver_objetivo(id):
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM objetivos WHERE id = %s AND eliminado_en IS NULL", (id,))
        obj = cur.fetchone()
    con.close()
    if obj is None:
        return jsonify({"error": "Objetivo no encontrado"}), 404
    return jsonify(obj)


@objetivos_bp.post("/api/objetivos")
def crear_objetivo():
    datos = request.get_json() or {}
    requeridos = ["sitio_id", "nombre", "tipo", "valor"]
    if not all(datos.get(c) for c in requeridos):
        return jsonify({"error": f"Requeridos: {', '.join(requeridos)}"}), 400
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute(
            "INSERT INTO objetivos (sitio_id, nombre, tipo, valor) VALUES (%s, %s, %s, %s)",
            (datos["sitio_id"], datos["nombre"], datos["tipo"], datos["valor"]),
        )
        nuevo_id = cur.lastrowid
    con.close()
    return jsonify({"mensaje": "Objetivo creado", "id": nuevo_id}), 201


@objetivos_bp.patch("/api/objetivos/<int:id>")
def editar_objetivo(id):
    datos = request.get_json() or {}
    cambios = {k: v for k, v in datos.items() if k in CAMPOS_EDITABLES}
    if not cambios:
        return jsonify({"error": "No hay campos validos"}), 400
    partes = ", ".join(f"{c} = %s" for c in cambios)
    valores = list(cambios.values()) + [id]
    con = conectar_mysql()
    with con.cursor() as cur:
        filas = cur.execute(
            f"UPDATE objetivos SET {partes} WHERE id = %s AND eliminado_en IS NULL", valores
        )
    con.close()
    if filas == 0:
        return jsonify({"error": "Objetivo no encontrado"}), 404
    return jsonify({"mensaje": "Objetivo actualizado"})


@objetivos_bp.delete("/api/objetivos/<int:id>")
def borrar_objetivo(id):
    con = conectar_mysql()
    with con.cursor() as cur:
        filas = cur.execute(
            "UPDATE objetivos SET eliminado_en = NOW() WHERE id = %s AND eliminado_en IS NULL", (id,)
        )
    con.close()
    if filas == 0:
        return jsonify({"error": "Objetivo no encontrado"}), 404
    return jsonify({"mensaje": "Objetivo marcado como borrado"})
