# Endpoint extra (aporte de Elias): une datos de los 3 motores.
# GET /api/estadisticas/<sitio_id> -> resumen con datos de MySQL, MongoDB y Redis.
from flask import Blueprint, jsonify
from db import conectar_mysql, mongo, r

estadisticas_bp = Blueprint("estadisticas", __name__)


@estadisticas_bp.get("/api/estadisticas/<int:sitio_id>")
def estadisticas(sitio_id):
    resumen = {"sitio_id": sitio_id}

    # Dato 1 (MySQL): el nombre del sitio
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT nombre FROM sitios WHERE id = %s AND eliminado_en IS NULL", (sitio_id,))
        row = cur.fetchone()
    con.close()
    resumen["sitio_nombre"] = row["nombre"] if row else None

    # Dato 2 (MongoDB): total de eventos registrados (no borrados)
    resumen["total_eventos"] = mongo["eventos"].count_documents(
        {"sitio_id": sitio_id, "eliminado": {"$ne": True}}
    )

    # Dato 3 (Redis): sesiones activas (las que tienen score en el sorted set)
    resumen["sesiones_activas"] = r.zcard(f"sitio:{sitio_id}:activas")

    return jsonify(resumen)
