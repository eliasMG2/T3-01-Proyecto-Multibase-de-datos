from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, render_template, request
from pymongo.errors import PyMongoError
from pymysql.err import MySQLError
from redis.exceptions import RedisError

from recursos.eventos import col
from recursos.sesiones import sesiones_registradas
from recursos.sitios import sitios_registrados

analiticas_bp = Blueprint("analiticas", __name__)


@analiticas_bp.get("/analiticas")
def panel():
    sitio_id = request.args.get("sitio_id", type=int)
    hoy = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    inicio = hoy - timedelta(days=6)
    filtro = {"eliminado": {"$ne": True}}
    if sitio_id is not None:
        filtro["sitio_id"] = {"$in": [sitio_id, str(sitio_id)]}

    try:
        sitios = sorted(sitios_registrados(), key=lambda sitio: sitio["nombre"].casefold())
        resultado = next(col.aggregate([
            {"$match": filtro},
            {"$facet": {
                "totales": [{"$group": {"_id": "$tipo", "total": {"$sum": 1}}}],
                "dias": [
                    {"$match": {
                        "fecha": {"$gte": inicio, "$lt": hoy + timedelta(days=1)},
                        "tipo": {"$in": ["visita", "clic"]},
                    }},
                    {"$group": {"_id": {
                        "dia": {"$dateToString": {"format": "%Y-%m-%d", "date": "$fecha"}},
                        "tipo": "$tipo",
                    }, "total": {"$sum": 1}}},
                ],
                "paginas": [
                    {"$match": {"tipo": "visita", "ruta": {"$type": "string", "$ne": ""}}},
                    {"$group": {"_id": "$ruta", "total": {"$sum": 1}}},
                    {"$sort": {"total": -1, "_id": 1}},
                    {"$limit": 6},
                ],
                "recientes": [
                    {"$sort": {"fecha": -1, "_id": -1}},
                    {"$limit": 8},
                    {"$project": {"tipo": 1, "ruta": 1, "fecha": 1, "sitio_id": 1}},
                ],
            }},
        ]))
        sesiones = sum(1 for _ in sesiones_registradas(str(sitio_id) if sitio_id is not None else None))
    except (MySQLError, PyMongoError, RedisError):
        current_app.logger.exception("No se pudieron cargar las analíticas")
        return render_template("analiticas.html", error=True, sitios=[], sitio_id=None), 503

    totales = {fila["_id"]: fila["total"] for fila in resultado["totales"] if isinstance(fila["_id"], str)}
    actividad = {(fila["_id"]["dia"], fila["_id"]["tipo"]): fila["total"] for fila in resultado["dias"]}
    dias = []
    for desplazamiento in range(7):
        fecha = inicio + timedelta(days=desplazamiento)
        clave = fecha.date().isoformat()
        dias.append({
            "fecha": fecha.strftime("%d/%m"),
            "visitas": actividad.get((clave, "visita"), 0),
            "clics": actividad.get((clave, "clic"), 0),
        })
    maximo = max(max(dia["visitas"], dia["clics"]) for dia in dias)
    nombres = {str(sitio["id"]): sitio["nombre"] for sitio in sitios}
    for evento in resultado["recientes"]:
        evento["sitio"] = nombres.get(str(evento.get("sitio_id")), "—")
        fecha = evento.get("fecha")
        evento["hora"] = fecha.strftime("%d/%m/%Y %H:%M") if isinstance(fecha, datetime) else "—"

    return render_template(
        "analiticas.html",
        sitios=sitios,
        sitio_id=sitio_id,
        visitas=totales.get("visita", 0),
        clics=totales.get("clic", 0),
        sesiones=sesiones,
        dias=dias,
        maximo=maximo,
        paginas=resultado["paginas"],
        recientes=resultado["recientes"],
    )
