# Pruebas de los recursos que me tocaron a mi (Elias):
#   - paginas y objetivos (MySQL)
#   - eventos (MongoDB)
# Uso: con Flask corriendo:    python tests/pruebas_elias.py
import urllib.request, json

BASE = "http://localhost:5000"

def req(m, ruta, datos=None):
    body = None if datos is None else json.dumps(datos).encode()
    r = urllib.request.Request(BASE+ruta, data=body, method=m,
        headers={"Content-Type": "application/json"} if body else {})
    try:
        with urllib.request.urlopen(r) as resp:
            t = resp.read().decode()
            return resp.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


# Necesito un sitio valido donde colgar lo demas
s,j = req("POST", "/api/usuarios", {"nombre":"Elias","email":"elias@x.com"})
s,j = req("POST", "/api/sitios", {"usuario_id":j["id"],"nombre":"Mi sitio","dominio":"ejemplo.com"})
sitio = j["id"]

print("--- PAGINAS ---")
s,j = req("POST","/api/paginas",{"sitio_id":sitio,"ruta":"/inicio","titulo":"Inicio"}); print("crear",s,j)
s,j = req("POST","/api/paginas",{"sitio_id":sitio,"ruta":"/productos","titulo":"Productos"}); pid=j["id"]
s,j = req("PATCH",f"/api/paginas/{pid}",{"titulo":"Catalogo"}); print("editar",s,j)
s,j = req("DELETE",f"/api/paginas/{pid}"); print("borrar",s,j)

print("--- OBJETIVOS ---")
s,j = req("POST","/api/objetivos",{"sitio_id":sitio,"nombre":"Suscripcion","tipo":"clic","valor":"#boton"}); print("crear",s,j)

print("--- EVENTOS (Mongo) ---")
s,j = req("POST","/api/eventos",{"sitio_id":sitio,"tipo":"visita","ruta":"/inicio"}); eid=j["id"]; print("crear visita",s,j)
s,j = req("POST","/api/eventos",{"sitio_id":sitio,"tipo":"clic","ruta":"/productos","datos":{"selector":"#comprar"}}); print("crear clic",s,j)
s,j = req("PATCH",f"/api/eventos/{eid}",{"etiquetas":["importante"],"revisado":True}); print("etiquetar",s,j)
# un patch con campo no editable debe fallar:
s,j = req("PATCH",f"/api/eventos/{eid}",{"tipo":"clic"}); print("no se puede editar tipo",s,j)

print("--- ESTADISTICAS (mi endpoint que une las 3 bases) ---")
s,j = req("GET",f"/api/estadisticas/{sitio}"); print(s,j)
