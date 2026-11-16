# Recurso: usuarios (vive en MySQL)
# Este archivo es el MOLDE: los demas recursos de MySQL se hacen igual.
from flask import Blueprint, request, jsonify
from db import conectar_mysql

usuarios_bp = Blueprint("usuarios", __name__)

CAMPOS_EDITABLES = ["nombre", "email", "rol"]


# GET: todos los usuarios que NO estan borrados
@usuarios_bp.get("/api/usuarios")
def listar_usuarios():
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM usuarios WHERE eliminado_en IS NULL")
        datos = cur.fetchall()
    con.close()
    return jsonify(datos)


# GET: un solo usuario
@usuarios_bp.get("/api/usuarios/<int:id>")
def ver_usuario(id):
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM usuarios WHERE id = %s AND eliminado_en IS NULL", (id,))
        usuario = cur.fetchone()
    con.close()
    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(usuario)


# POST: crear usuario
@usuarios_bp.post("/api/usuarios")
def crear_usuario():
    datos = request.get_json()
    if not datos or not datos.get("nombre") or not datos.get("email"):
        return jsonify({"error": "nombre y email son obligatorios"}), 400
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute(
            "INSERT INTO usuarios (nombre, email, rol) VALUES (%s, %s, %s)",
            (datos["nombre"], datos["email"], datos.get("rol", "analista")),
        )
        nuevo_id = cur.lastrowid
    con.close()
    return jsonify({"mensaje": "Usuario creado", "id": nuevo_id}), 201


# PATCH: modificar solo los campos que se manden
@usuarios_bp.patch("/api/usuarios/<int:id>")
def editar_usuario(id):
    datos = request.get_json() or {}
    cambios = {k: v for k, v in datos.items() if k in CAMPOS_EDITABLES}
    if not cambios:
        return jsonify({"error": "No hay campos validos para modificar"}), 400
    # arma algo como: "nombre = %s, rol = %s"
    partes = ", ".join(f"{campo} = %s" for campo in cambios)
    valores = list(cambios.values()) + [id]
    con = conectar_mysql()
    with con.cursor() as cur:
        filas = cur.execute(
            f"UPDATE usuarios SET {partes} WHERE id = %s AND eliminado_en IS NULL", valores
        )
    con.close()
    if filas == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"mensaje": "Usuario actualizado"})


# DELETE: borrado LOGICO, solo se marca la fecha en eliminado_en
@usuarios_bp.delete("/api/usuarios/<int:id>")
def borrar_usuario(id):
    con = conectar_mysql()
    with con.cursor() as cur:
        filas = cur.execute(
            "UPDATE usuarios SET eliminado_en = NOW() WHERE id = %s AND eliminado_en IS NULL", (id,)
        )
    con.close()
    if filas == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"mensaje": "Usuario marcado como borrado"})
