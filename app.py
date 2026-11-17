# Web Service multibase: analisis de visitas web
from flask import Flask, jsonify
from db import conectar_mysql, cliente_mongo, r

# Los 6 recursos del proyecto
from recursos.usuarios import usuarios_bp      # MySQL - Angel
from recursos.sitios import sitios_bp          # MySQL - Angel
from recursos.sesiones import sesiones_bp      # Redis - Angel
from recursos.paginas import paginas_bp        # MySQL - Elias
from recursos.objetivos import objetivos_bp    # MySQL - Elias
from recursos.eventos import eventos_bp
from recursos.estadisticas import estadisticas_bp   # endpoint extra que une las 3 bases (Elias)        # MongoDB - Elias

app = Flask(__name__)
app.json.ensure_ascii = False

app.register_blueprint(usuarios_bp)
app.register_blueprint(sitios_bp)
app.register_blueprint(sesiones_bp)
app.register_blueprint(paginas_bp)
app.register_blueprint(objetivos_bp)
app.register_blueprint(eventos_bp)
app.register_blueprint(estadisticas_bp)


@app.get("/api/salud")
def salud():
    estado = {}
    try:
        conectar_mysql().close(); estado["mysql"] = "ok"
    except Exception as e:
        estado["mysql"] = f"error: {e}"
    try:
        cliente_mongo.admin.command("ping"); estado["mongodb"] = "ok"
    except Exception as e:
        estado["mongodb"] = f"error: {e}"
    try:
        r.ping(); estado["redis"] = "ok"
    except Exception as e:
        estado["redis"] = f"error: {e}"
    return jsonify(estado)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
