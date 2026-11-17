# Mete datos de prueba en la base para poder probar el sistema completo.
# Uso: python seed.py
# (debe estar el Flask corriendo en otra terminal)
import urllib.request
import json

API = "http://localhost:5000"

def post(ruta, datos):
    req = urllib.request.Request(
        API + ruta,
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


print("1) Creando usuario de prueba...")
u = post("/api/usuarios", {"nombre": "Angel Alvarez", "email": "angel@tienda.com", "rol": "admin"})
print("   ->", u)

print("2) Creando sitio de prueba 'Mi Tienda'...")
s = post("/api/sitios", {"usuario_id": u["id"], "nombre": "Mi Tienda", "dominio": "mitienda.com"})
print("   ->", s)

print()
print("Listo. Ahora puedes abrir en el navegador:")
print(f"  {API}/api/usuarios")
print(f"  {API}/api/sitios")
print()
print(f"Abre {API}/ para registrar visitas y clics del sitio {s['id']}.")
