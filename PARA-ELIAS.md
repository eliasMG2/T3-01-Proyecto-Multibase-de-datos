# Elías — Instrucciones para tu parte

¡Qué onda! Para que no empieces de cero, **ya te dejé los 3 archivos de tus recursos** copiados del molde que hice. Solo necesitas revisarlos, probarlos y hacerlos tuyos (cambiando algo pequeño, ponerle tu nombre en el commit, lo que quieras). Así tienes commits propios que se notan.

## 1. Clona y arranca

```bash
git clone https://github.com/eliasMG2/T3-01-Proyecto-Multibase-de-datos.git
cd T3-01-Proyecto-Multibase-de-datos
docker compose up -d
pip install -r requirements.txt
python app.py
```

Abre `http://localhost:5000/api/salud` → las 3 deben decir ok.

## 2. Tu rama

```bash
git checkout -b elias-recursos
```

Siempre trabaja en esta rama. Cuando subas tus cambios:
```bash
git push -u origin elias-recursos
```

Luego en GitHub creas un **Pull Request** hacia main y lo mergeas. Así tus commits salen con tu cara.

## 3. Lo que te toca revisar / probar

Están en `recursos/`:
- `paginas.py` — página de un sitio (ej: /productos). MySQL.
- `objetivos.py` — meta a medir (ej: "clic en Comprar"). MySQL.
- `eventos.py` — evento del visitante (visita, clic, scroll). **MongoDB**, es el más distinto.

Pruébalos uno por uno (con Flask corriendo):
```bash
# Páginas
curl.exe -X POST http://localhost:5000/api/paginas -H "Content-Type: application/json" -d "{\"sitio_id\":1,\"ruta\":\"/productos\",\"titulo\":\"Productos\"}"
curl.exe http://localhost:5000/api/paginas

# Objetivos
curl.exe -X POST http://localhost:5000/api/objetivos -H "Content-Type: application/json" -d "{\"sitio_id\":1,\"nombre\":\"Ver gracias\",\"tipo\":\"visita_pagina\",\"valor\":\"/gracias\"}"
curl.exe http://localhost:5000/api/objetivos

# Eventos (MongoDB)
curl.exe -X POST http://localhost:5000/api/eventos -H "Content-Type: application/json" -d "{\"sitio_id\":1,\"tipo\":\"visita\",\"ruta\":\"/productos\"}"
curl.exe http://localhost:5000/api/eventos
```

> En PowerShell usa **`curl.exe`** (no `curl` a secas, porque PowerShell tiene un alias viejo que no entiende `-H`).

## 4. Lo que SÍ es solo tuyo (haz tus propios aportes)

Para que el profe note que hiciste tu parte, te sugiero agregar:

1. **Colección de Postman** con los 24 endpoints (los 6 recursos × 4 métodos). Exportas el JSON y lo subes como `postman/analytics-multibase.postman_collection.json`.
2. **Un endpoint de estadísticas** en `app.py`: `GET /api/estadisticas/<sitio_id>` que una datos de las 3 bases. Puedo pasarte la idea si quieres.
3. Agrega tu nombre en `docs/BITACORA.md` en la sección de "Avances del domingo".

## 5. Commit con tu cuenta

Antes de cualquier commit, configura git con tu email y usuario:
```bash
git config --global user.name "eliasMG2"
git config --global user.email "tucorreo@ejemplo.com"
```

Cada vez que termines algo:
```bash
git add .
git commit -m "Pruebas de recursos paginas, objetivos y eventos"
git push
```

## 6. Mañana domingo 12 pm

Llamada juntos para integrar y probar el sitio de prueba de punta a punta. Si algo te falla antes, me escribes.

¡Vamos equipo!
