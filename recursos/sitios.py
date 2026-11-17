# Recurso: sitios (vive en MySQL)
# Un sitio = una pagina web que vamos a monitorear (ej: mitienda.com)
from flask import Blueprint, request, jsonify
from db import conectar_mysql

sitios_bp = Blueprint("sitios", __name__)

CAMPOS_EDITABLES = ["nombre", "dominio"]


def sitios_registrados():
    with conectar_mysql() as con, con.cursor() as cur:
        cur.execute("SELECT * FROM sitios WHERE eliminado_en IS NULL")
        return cur.fetchall()


@sitios_bp.get("/api/sitios")
def listar_sitios():
    return jsonify(sitios_registrados())


@sitios_bp.get("/api/sitios/<int:id>")
def ver_sitio(id):
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM sitios WHERE id = %s AND eliminado_en IS NULL", (id,))
        sitio = cur.fetchone()
    con.close()
    if sitio is None:
        return jsonify({"error": "Sitio no encontrado"}), 404
    return jsonify(sitio)


@sitios_bp.post("/api/sitios")
def crear_sitio():
    datos = request.get_json() or {}
    if not datos.get("usuario_id") or not datos.get("nombre") or not datos.get("dominio"):
        return jsonify({"error": "usuario_id, nombre y dominio son obligatorios"}), 400
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute(
            "INSERT INTO sitios (usuario_id, nombre, dominio) VALUES (%s, %s, %s)",
            (datos["usuario_id"], datos["nombre"], datos["dominio"]),
        )
        nuevo_id = cur.lastrowid
    con.close()
    return jsonify({"mensaje": "Sitio creado", "id": nuevo_id}), 201


@sitios_bp.patch("/api/sitios/<int:id>")
def editar_sitio(id):
    datos = request.get_json() or {}
    cambios = {k: v for k, v in datos.items() if k in CAMPOS_EDITABLES}
    if not cambios:
        return jsonify({"error": "No hay campos validos para modificar"}), 400
    partes = ", ".join(f"{c} = %s" for c in cambios)
    valores = list(cambios.values()) + [id]
    con = conectar_mysql()
    with con.cursor() as cur:
        filas = cur.execute(
            f"UPDATE sitios SET {partes} WHERE id = %s AND eliminado_en IS NULL", valores
        )
    con.close()
    if filas == 0:
        return jsonify({"error": "Sitio no encontrado"}), 404
    return jsonify({"mensaje": "Sitio actualizado"})


@sitios_bp.delete("/api/sitios/<int:id>")
def borrar_sitio(id):
    con = conectar_mysql()
    with con.cursor() as cur:
        filas = cur.execute(
            "UPDATE sitios SET eliminado_en = NOW() WHERE id = %s AND eliminado_en IS NULL", (id,)
        )
    con.close()
    if filas == 0:
        return jsonify({"error": "Sitio no encontrado"}), 404
    return jsonify({"mensaje": "Sitio marcado como borrado"})
