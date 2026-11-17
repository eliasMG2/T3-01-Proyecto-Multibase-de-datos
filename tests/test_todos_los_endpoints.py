# Prueba los 24 endpoints del proyecto + verifica que el borrado logico funcione.
# Uso: con Flask corriendo en otra terminal:
#   python tests/test_todos_los_endpoints.py
import urllib.request, urllib.error, json, sys, time

BASE = "http://localhost:5000"

def req(metodo, ruta, datos=None):
    url = BASE + ruta
    cuerpo = None if datos is None else json.dumps(datos).encode("utf-8")
    hdrs = {"Content-Type": "application/json"} if cuerpo else {}
    r = urllib.request.Request(url, data=cuerpo, method=metodo, headers=hdrs)
    try:
        with urllib.request.urlopen(r) as resp:
            texto = resp.read().decode()
            return resp.status, (json.loads(texto) if texto else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error_cliente": str(e)}

ok = fail = 0
def check(nombre, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1; print(f"  OK  {nombre}")
    else:
        fail += 1; print(f"  FAIL {nombre}  {extra}")

print("=== 0. Salud de las 3 bases ===")
s, j = req("GET", "/api/salud")
check(f"GET /api/salud -> 200 ({j})", s == 200 and j.get("mysql") == "ok" and j.get("mongodb") == "ok" and j.get("redis") == "ok")

# --- USUARIOS ---
print("\n=== 1. USUARIOS (MySQL) ===")
email = f"test{int(time.time())}@x.com"
s, j = req("POST", "/api/usuarios", {"nombre": "Prueba", "email": email})
uid = j.get("id"); check("POST usuario", s == 201 and uid, j)
check("GET lista usuarios", req("GET", "/api/usuarios")[0] == 200)
check("GET /api/usuarios/:id", req("GET", f"/api/usuarios/{uid}")[0] == 200)
check("PATCH usuario", req("PATCH", f"/api/usuarios/{uid}", {"rol": "admin"})[0] == 200)
check("DELETE usuario (borrado logico)", req("DELETE", f"/api/usuarios/{uid}")[0] == 200)
check("GET usuario tras borrar -> 404", req("GET", f"/api/usuarios/{uid}")[0] == 404)

# --- SITIOS ---
print("\n=== 2. SITIOS (MySQL) ===")
s, j = req("POST", "/api/usuarios", {"nombre": "Dueno", "email": f"d{int(time.time())}@x.com"}); dueno = j["id"]
s, j = req("POST", "/api/sitios", {"usuario_id": dueno, "nombre": "SitioTest", "dominio": "test.com"})
sid = j.get("id"); check("POST sitio", s == 201 and sid, j)
check("GET lista sitios", req("GET", "/api/sitios")[0] == 200)
check("GET /api/sitios/:id", req("GET", f"/api/sitios/{sid}")[0] == 200)
check("PATCH sitio", req("PATCH", f"/api/sitios/{sid}", {"nombre": "SitioTest2"})[0] == 200)
check("DELETE sitio (borrado logico)", req("DELETE", f"/api/sitios/{sid}")[0] == 200)
check("GET sitio tras borrar -> 404", req("GET", f"/api/sitios/{sid}")[0] == 404)

# sitio vivo para probar lo demas
s, j = req("POST", "/api/sitios", {"usuario_id": dueno, "nombre": "SitioVivo", "dominio": "vivo.com"}); sid = j["id"]

# --- PAGINAS ---
print("\n=== 3. PAGINAS (MySQL) ===")
s, j = req("POST", "/api/paginas", {"sitio_id": sid, "ruta": "/test", "titulo": "Prueba"})
pid = j.get("id"); check("POST pagina", s == 201 and pid, j)
check("GET lista paginas", req("GET", "/api/paginas")[0] == 200)
check("GET /api/paginas/:id", req("GET", f"/api/paginas/{pid}")[0] == 200)
check("PATCH pagina", req("PATCH", f"/api/paginas/{pid}", {"titulo": "Nuevo"})[0] == 200)
check("DELETE pagina (borrado logico)", req("DELETE", f"/api/paginas/{pid}")[0] == 200)
check("GET pagina tras borrar -> 404", req("GET", f"/api/paginas/{pid}")[0] == 404)

# --- OBJETIVOS ---
print("\n=== 4. OBJETIVOS (MySQL) ===")
s, j = req("POST", "/api/objetivos", {"sitio_id": sid, "nombre": "C", "tipo": "visita_pagina", "valor": "/gracias"})
oid = j.get("id"); check("POST objetivo", s == 201 and oid, j)
check("GET lista objetivos", req("GET", "/api/objetivos")[0] == 200)
check("GET /api/objetivos/:id", req("GET", f"/api/objetivos/{oid}")[0] == 200)
check("PATCH objetivo", req("PATCH", f"/api/objetivos/{oid}", {"nombre": "C2"})[0] == 200)
check("DELETE objetivo (borrado logico)", req("DELETE", f"/api/objetivos/{oid}")[0] == 200)
check("GET objetivo tras borrar -> 404", req("GET", f"/api/objetivos/{oid}")[0] == 404)

# --- EVENTOS ---
print("\n=== 5. EVENTOS (MongoDB) ===")
s, j = req("POST", "/api/eventos", {"sitio_id": sid, "tipo": "visita", "ruta": "/test"})
eid = j.get("id"); check("POST evento", s == 201 and eid, j)
check("GET lista eventos", req("GET", "/api/eventos")[0] == 200)
check("GET /api/eventos/:id", req("GET", f"/api/eventos/{eid}")[0] == 200)
check("PATCH evento (etiquetas y revisado)", req("PATCH", f"/api/eventos/{eid}", {"revisado": True, "etiquetas": ["p"]})[0] == 200)
check("PATCH evento rechaza campo no editable", req("PATCH", f"/api/eventos/{eid}", {"tipo": "clic"})[0] == 400)
check("DELETE evento (borrado logico)", req("DELETE", f"/api/eventos/{eid}")[0] == 200)
check("GET evento tras borrar -> 404", req("GET", f"/api/eventos/{eid}")[0] == 404)

# --- SESIONES ---
print("\n=== 6. SESIONES (Redis) ===")
s, j = req("POST", "/api/sesiones", {"sitio_id": sid, "visitante_id": "v-test"})
ses = j.get("id"); check("POST sesion", s == 201 and ses, j)
check("GET lista sesiones", req("GET", "/api/sesiones")[0] == 200)
check("GET /api/sesiones/:id", req("GET", f"/api/sesiones/{ses}")[0] == 200)
check("PATCH sesion", req("PATCH", f"/api/sesiones/{ses}", {"suma_pagina": True})[0] == 200)
check("DELETE sesion (borrado logico)", req("DELETE", f"/api/sesiones/{ses}")[0] == 200)
check("GET sesion tras borrar -> 404", req("GET", f"/api/sesiones/{ses}")[0] == 404)

# --- extras ---
print("\n=== 7. Extras ===")
s, j = req("GET", f"/api/estadisticas/{sid}")
check("GET /api/estadisticas/:sitio_id (une las 3 bases)", s == 200, j)

print(f"\n=== RESULTADO: {ok} OK · {fail} FAIL ===")
sys.exit(0 if fail == 0 else 1)
