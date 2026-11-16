# Recurso: paginas (vive en MySQL)
# Una pagina = cada URL de un sitio que se monitorea (ej: /productos, /contacto).
#
# ⚠️ Para Elias: este archivo ya esta armado. Nomas revisa que entiendas cada linea.
# Si quieres partir desde cero, puedes copiar recursos/usuarios.py y cambiar nombres.
from flask import Blueprint, request, jsonify
from db import conectar_mysql

paginas_bp = Blueprint("paginas", __name__)

CAMPOS_EDITABLES = ["ruta", "titulo"]


@paginas_bp.get("/api/paginas")
def listar_paginas():
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM paginas WHERE eliminado_en IS NULL")
        datos = cur.fetchall()
    con.close()
    return jsonify(datos)


@paginas_bp.get("/api/paginas/<int:id>")
def ver_pagina(id):
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM paginas WHERE id = %s AND eliminado_en IS NULL", (id,))
        pagina = cur.fetchone()
    con.close()
    if pagina is None:
        return jsonify({"error": "Pagina no encontrada"}), 404
    return jsonify(pagina)


@paginas_bp.post("/api/paginas")
def crear_pagina():
    datos = request.get_json() or {}
    if not datos.get("sitio_id") or not datos.get("ruta"):
        return jsonify({"error": "sitio_id y ruta son obligatorios"}), 400
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute(
            "INSERT INTO paginas (sitio_id, ruta, titulo) VALUES (%s, %s, %s)",
            (datos["sitio_id"], datos["ruta"], datos.get("titulo", "")),
        )
        nuevo_id = cur.lastrowid
    con.close()
    return jsonify({"mensaje": "Pagina creada", "id": nuevo_id}), 201


@paginas_bp.patch("/api/paginas/<int:id>")
def editar_pagina(id):
    datos = request.get_json() or {}
    cambios = {k: v for k, v in datos.items() if k in CAMPOS_EDITABLES}
    if not cambios:
        return jsonify({"error": "No hay campos validos"}), 400
    partes = ", ".join(f"{c} = %s" for c in cambios)
    valores = list(cambios.values()) + [id]
    con = conectar_mysql()
    with con.cursor() as cur:
        filas = cur.execute(
            f"UPDATE paginas SET {partes} WHERE id = %s AND eliminado_en IS NULL", valores
        )
    con.close()
    if filas == 0:
        return jsonify({"error": "Pagina no encontrada"}), 404
    return jsonify({"mensaje": "Pagina actualizada"})


@paginas_bp.delete("/api/paginas/<int:id>")
def borrar_pagina(id):
    con = conectar_mysql()
    with con.cursor() as cur:
        filas = cur.execute(
            "UPDATE paginas SET eliminado_en = NOW() WHERE id = %s AND eliminado_en IS NULL", (id,)
        )
    con.close()
    if filas == 0:
        return jsonify({"error": "Pagina no encontrada"}), 404
    return jsonify({"mensaje": "Pagina marcada como borrada"})
