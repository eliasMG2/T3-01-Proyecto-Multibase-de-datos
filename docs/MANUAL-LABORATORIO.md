# Manual de Laboratorio — Proyecto Multibase T3-01

**Materia:** Tópicos de Bases de Datos (IFF-1026) · 2° Unidad
**Profesor:** Francisco Cervantes Zambrano · Instituto Tecnológico de Colima
**Alumnos:** Ángel Salvador Álvarez Fernández (23460501) · Elías Meléndez Guzmán
**Entrega:** martes 17 de noviembre de 2026, 23:59

Este documento explica **todo** el proyecto paso a paso: para qué sirve cada archivo, qué significa cada línea de código importante, qué comandos se usaron y por qué. Está escrito para que cualquiera de los dos del equipo pueda abrirlo, leerlo y defender el trabajo frente al profesor.

---

## Parte I — Conceptos base

### 1. ¿Qué es un sistema multibase de datos?

En clase (transcripción del 6 de noviembre) el profesor lo explicó así: *"Se refiere a aquellos sistemas que no solo utilizan una base de datos, sino que utilizan múltiples motores de base de datos para resolver problemas. Cada motor tiene un propósito distinto: unos pueden usarse como cachés, otros como almacenamiento permanente, otros para datos completos y otros para datos complejos"*.

La idea es que, en lugar de forzar a un solo motor a hacerlo todo, se usan **varios motores especializados** y cada uno hace lo que mejor sabe hacer. En nuestro proyecto:

| Motor | Tipo | Qué hace mejor | Qué le toca |
|---|---|---|---|
| **MySQL** | Relacional (SQL) | Datos muy estructurados, relaciones, transacciones | Usuarios, sitios, páginas, objetivos |
| **MongoDB** | NoSQL documental | Datos con forma variable, consultas flexibles | Eventos de visitantes |
| **Redis** | Clave-valor en memoria | Lectura y escritura ultra rápidas, contadores, sesiones | Sesiones activas, contadores |

### 2. ¿Qué es un Web Service?

Es un programa que corre en un servidor y **responde por HTTP** (el mismo protocolo que usan las páginas web). En lugar de devolver HTML para que lo vea una persona, devuelve **datos en JSON** para que los use otro programa (una aplicación móvil, un panel web, otro servicio).

Nuestro Web Service es `app.py`. Se arranca con `python app.py` y queda escuchando en el puerto 5000. Se le hacen peticiones a URLs como `http://localhost:5000/api/usuarios` y responde con JSON.

### 3. ¿Qué son GET, POST, PATCH y DELETE?

Son los **verbos HTTP**. Cada uno es una acción distinta sobre un recurso:

| Verbo | Qué significa | Ejemplo |
|---|---|---|
| **GET** | Leer / consultar | Dame la lista de usuarios |
| **POST** | Crear | Crea un nuevo usuario |
| **PATCH** | Modificar parcialmente | Cambia solo el rol del usuario 1 |
| **DELETE** | Borrar | Borra el usuario 1 |

Juntos forman lo que se llama una **API REST**. El profesor pidió que **los 6 recursos** del proyecto tengan los 4 métodos, lo que da **6 × 4 = 24 endpoints** en total.

### 4. ¿Qué es un "recurso"?

Cuando el compañero preguntó qué era un recurso, el profesor contestó (transcripción del 6 de noviembre): *"Si usted tiene usuarios, artículos, ventas, categorías, proveedores, sucursales, cada uno de esos es un recurso y cada uno va a tener su propio GET, POST, PATCH y DELETE"*.

Un recurso es básicamente **un tipo de cosa** que la aplicación maneja. En nuestro caso: usuarios, sitios, páginas, objetivos, eventos y sesiones son los seis recursos.

### 5. ¿Qué es el "borrado lógico"?

Cuando el profesor dijo *"el borrado de los registros deberá ser lógico, no se elimina el registro, sólo se marca como borrado"*, se refiere a esto:

- **Borrado físico (lo normal):** El registro se elimina de la base. Se pierde para siempre.
- **Borrado lógico (lo que pide):** El registro se queda en la base, pero se le añade una marca (una columna, un campo, una bandera) que dice "este está borrado". Las consultas normales lo ignoran, pero el dato sigue ahí por si hay que recuperarlo o auditarlo.

Es como tachar un nombre en una lista con lápiz en vez de arrancar la hoja. Ventaja: nunca se pierde información y se puede saber quién borró qué y cuándo.

### 6. ¿Qué es Docker y por qué lo usamos?

Docker es un programa que permite correr aplicaciones (como MySQL, MongoDB o Redis) **dentro de contenedores aislados**, sin tener que instalarlas directamente en la computadora. Cada contenedor es como una mini-computadora virtual con una sola aplicación corriendo dentro.

En nuestro proyecto, en vez de instalar MySQL, MongoDB y Redis en Windows (cada uno con su propio instalador, sus propios conflictos, sus propios puertos), levantamos los tres de un jalón con el archivo `docker-compose.yml`, y cuando terminemos los apagamos con un solo comando. Ya no quedan procesos sueltos en la computadora.

El profesor ya lo usó en el tema 1 cuando montamos MySQL, MongoDB y Redis por separado en las prácticas pasadas.

---

## Parte II — Arquitectura del proyecto

```
NAVEGADOR DEL VISITANTE                     TU COMPUTADORA
┌──────────────────────┐                   ┌───────────────────────────┐
│  sitio-prueba/       │   fetch (JSON)    │   Flask (app.py) :5000    │
│  index.html          │ ────────────────> │   ├─ /api/usuarios        │
│  productos.html      │                   │   ├─ /api/sitios          │
│  contacto.html       │                   │   ├─ /api/paginas         │
│  tracker.js          │                   │   ├─ /api/objetivos       │
└──────────────────────┘                   │   ├─ /api/eventos         │
                                           │   ├─ /api/sesiones        │
                                           │   └─ /api/salud           │
                                           └───┬──────────┬──────────┬─┘
                                               │          │          │
                                          ┌────▼──┐  ┌────▼───┐  ┌──▼────┐
                                          │ MySQL │  │ Mongo  │  │ Redis │
                                          │ :3307 │  │ :27018 │  │ :6380 │
                                          └───────┘  └────────┘  └───────┘
                                          Docker Compose (docker-compose.yml)
```

**Flujo típico (cuando un visitante entra a /productos):**

1. El navegador carga `productos.html` y con él el script `tracker.js`.
2. `tracker.js` ve que no hay sesión abierta y hace `POST /api/sesiones` → Flask guarda la sesión en **Redis**.
3. `tracker.js` dispara el evento "visita" y hace `POST /api/eventos` → Flask guarda el evento en **MongoDB**.
4. Si el visitante da clic en un botón, `tracker.js` hace otro `POST /api/eventos` → otro documento en MongoDB.
5. Cuando un administrador abre el panel y lista `/api/usuarios` → Flask consulta **MySQL**.

---

## Parte III — Archivo por archivo

Esta sección explica qué hace cada archivo del proyecto y por qué está donde está.

```
analytics-multibase/
├── docker-compose.yml      ← Levanta las 3 bases
├── schema.sql              ← Crea las 4 tablas de MySQL
├── requirements.txt        ← Librerías de Python que se necesitan
├── .gitignore              ← Qué archivos Git debe ignorar
├── db.py                   ← Conexiones a los 3 motores
├── app.py                  ← Arranca el Web Service (Flask)
├── seed.py                 ← Mete datos de prueba
├── README.md               ← Instrucciones para instalar
├── PARA-ELIAS.md           ← Guía personal para el compañero
├── recursos/               ← Aquí vive cada recurso por separado
│   ├── usuarios.py         ← Recurso 1 (MySQL)
│   ├── sitios.py           ← Recurso 2 (MySQL)
│   ├── paginas.py          ← Recurso 3 (MySQL)
│   ├── objetivos.py        ← Recurso 4 (MySQL)
│   ├── eventos.py          ← Recurso 5 (MongoDB)
│   └── sesiones.py         ← Recurso 6 (Redis)
├── sitio-prueba/           ← El sitio falso que manda eventos
│   ├── index.html
│   ├── productos.html
│   ├── contacto.html
│   └── tracker.js          ← El "espía" que manda las visitas
└── docs/
    ├── BITACORA.md
    └── MANUAL-LABORATORIO.md  (este archivo)
```

### A. `docker-compose.yml` — levantar las 3 bases

```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: analytics-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: analytics
    ports:
      - "3307:3306"
    volumes:
      - ./schema.sql:/docker-entrypoint-initdb.d/schema.sql

  mongo:
    image: mongo:latest
    container_name: analytics-mongo
    ports:
      - "27018:27017"

  redis:
    image: redis:latest
    container_name: analytics-redis
    ports:
      - "6380:6379"
```

**Línea por línea:**

- `services:` → cada apartado debajo es un contenedor distinto (una "aplicación").
- `image: mysql:8.0` → qué imagen bajar de Docker Hub. Es como decir "quiero MySQL versión 8.0".
- `container_name:` → el nombre que verás en Docker Desktop. Les puse "analytics-*" para distinguirlos de los contenedores de las prácticas anteriores.
- `environment:` → variables de entorno. MySQL necesita saber la contraseña del usuario root y el nombre de la base inicial.
- `ports: - "3307:3306"` → esto es clave. Significa "el puerto 3306 del contenedor (donde MySQL escucha por dentro) se asoma al puerto 3307 de mi computadora". **Usamos 3307 (y no 3306) a propósito** para no chocar con el contenedor de MySQL de la práctica T1-03 del clúster, que usa el 3306.
- `volumes: - ./schema.sql:/docker-entrypoint-initdb.d/schema.sql` → esto hace que MySQL, al arrancar por primera vez, ejecute automáticamente el archivo `schema.sql` y cree las tablas solas. No tenemos que entrar a MySQL a mano.

Para arrancar los 3: `docker compose up -d` (la `-d` significa "detached", en segundo plano).
Para apagarlos: `docker compose down`.

### B. `schema.sql` — las 4 tablas de MySQL

```sql
CREATE DATABASE IF NOT EXISTS analytics;
USE analytics;

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL,
  rol VARCHAR(20) NOT NULL DEFAULT 'analista',
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  eliminado_en DATETIME NULL
);
```

**Lo clave de este archivo:** cada tabla tiene una columna llamada **`eliminado_en`** de tipo `DATETIME NULL`. Mientras esa columna esté en `NULL`, el registro está vivo. Cuando le ponemos la fecha de hoy, queda **borrado lógicamente**.

Esto es lo que resuelve el requisito del profesor para las 4 tablas de MySQL.

### C. `db.py` — las 3 conexiones

```python
import pymysql
from pymongo import MongoClient
import redis

def conectar_mysql():
    return pymysql.connect(
        host="localhost", port=3307,
        user="root", password="root123",
        database="analytics",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        charset="utf8mb4",
    )

cliente_mongo = MongoClient("mongodb://localhost:27018", serverSelectionTimeoutMS=3000)
mongo = cliente_mongo["analytics"]

r = redis.Redis(host="localhost", port=6380, decode_responses=True)
```

**Línea por línea:**

- `pymysql`, `pymongo`, `redis` → son las librerías de Python que se hablan con cada motor.
- `conectar_mysql()` es una **función** (no una variable). ¿Por qué? Porque a MySQL se le debe pedir una conexión fresca cada vez que la vamos a usar, y cerrarla al terminar. Si dejáramos una sola conexión global abierta, se podría caer y no se recuperaría.
- `cursorclass=pymysql.cursors.DictCursor` → hace que MySQL devuelva las filas como diccionarios de Python (`{"id": 1, "nombre": "..."}`) en vez de tuplas. Es mucho más cómodo para convertir a JSON.
- `autocommit=True` → cada cambio se guarda al instante, sin tener que llamar a `commit()`. Menos código y menos errores.
- `cliente_mongo` sí es una variable global porque MongoDB se puede usar sin problema con un solo cliente para toda la app.
- `r = redis.Redis(..., decode_responses=True)` → el `decode_responses=True` hace que Redis devuelva texto (`"hola"`) en vez de bytes (`b"hola"`).

### D. `app.py` — el Web Service

```python
from flask import Flask, jsonify
from db import conectar_mysql, cliente_mongo, r

from recursos.usuarios import usuarios_bp
from recursos.sitios import sitios_bp
from recursos.sesiones import sesiones_bp
from recursos.paginas import paginas_bp
from recursos.objetivos import objetivos_bp
from recursos.eventos import eventos_bp

app = Flask(__name__)
app.json.ensure_ascii = False

app.register_blueprint(usuarios_bp)
# ... los otros 5
```

**Conceptos:**

- `Flask` es el framework que convierte Python en un servidor web. Es muy ligero: unas 15 líneas y ya tienes un servidor contestando peticiones.
- Los **Blueprints** son como mini-apps que se enchufan al Flask principal. Cada recurso vive en su propio archivo con su propio Blueprint, y aquí los registramos todos. **Ventaja práctica:** mientras Ángel trabaja en `usuarios.py`, Elías puede estar trabajando en `eventos.py` sin tocar el mismo archivo. Se evitan conflictos al hacer merge en Git.
- `app.json.ensure_ascii = False` → para que los acentos (á, é, í) se vean bien en el JSON y no como `á`.
- El endpoint `/api/salud` es un **health check**: pregunta a las 3 bases "¿estás viva?" y regresa un JSON con el estado. Se usa para saber al instante si algo falló.

### E. `recursos/usuarios.py` — el molde CRUD

Este es el archivo más importante de entender, porque los otros 3 recursos de MySQL (sitios, paginas, objetivos) son **copias de este** cambiando solo el nombre de la tabla y los campos.

**GET lista:**
```python
@usuarios_bp.get("/api/usuarios")
def listar_usuarios():
    con = conectar_mysql()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM usuarios WHERE eliminado_en IS NULL")
        datos = cur.fetchall()
    con.close()
    return jsonify(datos)
```
- El decorador `@usuarios_bp.get(...)` registra la función para que responda a peticiones GET en esa URL.
- `WHERE eliminado_en IS NULL` → esta es la clave del borrado lógico en MySQL: **nunca devolvemos los que están marcados como borrados.**
- `jsonify` convierte la lista de diccionarios en JSON.

**POST (crear):**
```python
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
```
- `request.get_json()` lee el cuerpo de la petición (el JSON que mandó el cliente).
- Validación básica: si falta nombre o email, regresa `400 Bad Request`.
- Uso de **parámetros** `%s` en lugar de concatenar texto. Esto evita **inyección SQL**, que es un ataque donde alguien mete código malicioso en los datos. **Nunca se concatenan datos del usuario directamente en una consulta SQL.**
- `cur.lastrowid` → el id autogenerado por MySQL.
- `201` es el código HTTP para "Creado correctamente".

**PATCH (modificar parcial):**
```python
@usuarios_bp.patch("/api/usuarios/<int:id>")
def editar_usuario(id):
    datos = request.get_json() or {}
    cambios = {k: v for k, v in datos.items() if k in CAMPOS_EDITABLES}
    if not cambios:
        return jsonify({"error": "No hay campos validos para modificar"}), 400
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
```
- `<int:id>` en la ruta → captura un número de la URL. Si el cliente pide `/api/usuarios/5`, el `id` vale 5.
- La lista `CAMPOS_EDITABLES` es una **lista blanca**: solo los campos que están ahí se pueden modificar. Si alguien manda `{"rol":"admin", "id":999, "creado_en":"ayer"}`, solo se aplica `rol`. Protege la integridad de los datos.
- Se arma el UPDATE dinámicamente para modificar solo los campos que el cliente envió.
- El filtro `AND eliminado_en IS NULL` evita que se puedan modificar registros borrados.

**DELETE (borrado lógico):**
```python
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
```
- **Fíjate bien: esto NO es un `DELETE FROM`, es un `UPDATE ... SET eliminado_en = NOW()`.** Ese es exactamente el requisito del profesor. El registro se queda, solo se marca.
- Si lo borramos otra vez, `filas == 0` y respondemos 404, porque el filtro `AND eliminado_en IS NULL` ya no lo encuentra.

### F. `recursos/eventos.py` — el recurso más diferente (MongoDB)

MongoDB no usa SQL ni cursores. Usa métodos como `insert_one`, `find`, `update_one`.

```python
@eventos_bp.post("/api/eventos")
def crear_evento():
    datos = request.get_json() or {}
    if not datos.get("tipo") or not datos.get("sitio_id"):
        return jsonify({"error": "tipo y sitio_id son obligatorios"}), 400
    datos["fecha"] = datetime.utcnow()
    datos["eliminado"] = False
    datos.setdefault("etiquetas", [])
    datos.setdefault("revisado", False)
    resultado = col.insert_one(datos)
    return jsonify({"mensaje": "Evento registrado", "id": str(resultado.inserted_id)}), 201
```
- `col.insert_one(datos)` guarda el documento tal cual. **Fíjate que MongoDB no requiere que todos los documentos tengan los mismos campos.** Un evento tipo "visita" lleva `ruta`, uno tipo "clic" lleva `selector` y `texto`, uno tipo "scroll" lleva `porcentaje`. **Esa flexibilidad es justamente la razón por la que los eventos viven en MongoDB y no en MySQL** (si estuvieran en MySQL habría que crear una tabla con columnas para cada posibilidad, llenas de nulos).
- `resultado.inserted_id` es un `ObjectId` (identificador único que MongoDB asigna). Como no es texto normal, lo convertimos con `str(...)` para que se pueda mandar en JSON.
- `datos["eliminado"] = False` → igual que en MySQL, cada documento lleva su marca de borrado lógico.

**Regla especial del PATCH:**
```python
CAMPOS_EDITABLES = ["etiquetas", "revisado"]
```
A diferencia de un usuario (donde se puede cambiar el nombre, rol, etc.), un **evento es un hecho ocurrido**: la visita pasó, el clic pasó. No tiene sentido "editarlo". Solo permitimos **etiquetarlo** (clasificarlo) o **marcarlo como revisado**. Esto es una decisión de diseño que vale la pena explicar al profesor si pregunta.

**DELETE en Mongo:**
```python
r = col.update_one(
    {"_id": ObjectId(id), "eliminado": {"$ne": True}},
    {"$set": {"eliminado": True, "eliminado_en": datetime.utcnow()}}
)
```
- `$set` modifica solo los campos especificados.
- `$ne: True` significa "donde `eliminado` no sea True" (es decir, los no borrados).
- Borrado lógico cumplido también aquí.

### G. `recursos/sesiones.py` — el recurso más delicado (Redis)

Redis no tiene tablas. Guarda datos en estructuras simples: strings, listas, hashes, sorted sets.

Una sesión vive como un **HASH** (algo parecido a un diccionario) con clave `sesion:{id}`:
```python
r.hset(f"sesion:{sesion_id}", mapping={
    "id": sesion_id,
    "sitio_id": datos["sitio_id"],
    "visitante_id": datos["visitante_id"],
    "inicio": ahora,
    "ultima_actividad": ahora,
    "paginas_vistas": 1,
    "estado": "activa",
    "eliminado": 0,
})
r.zadd(f"sitio:{datos['sitio_id']}:activas", {sesion_id: ahora})
```

Y además se mete al **sorted set** `sitio:{id}:activas`, donde el score es el timestamp de la última actividad. Esto permite, con una sola consulta `ZCOUNT`, saber cuántas sesiones están activas ahora mismo (las que tienen actividad en los últimos 5 minutos).

**IMPORTANTE — el borrado lógico en Redis es el más delicado:**

```python
r.hset(f"sesion:{id}", mapping={
    "eliminado": 1,
    "estado": "cerrada",
    "eliminado_en": time.time(),
})
r.zrem(f"sitio:{datos['sitio_id']}:activas", id)
```

Fíjate que **NO usamos `DEL`** (que sería el borrado físico en Redis). Solo cambiamos el campo `eliminado` del hash a 1 y lo sacamos del sorted set de activas.

**Y más importante aún: no le ponemos `EXPIRE` (TTL)** al hash. Si lo hiciéramos, Redis borraría físicamente la sesión cuando caducara el TTL, y romperíamos la regla del borrado lógico. En Redis, para cumplir el requisito del profesor, hay que renunciar a la expiración automática y manejar la "cierre" de sesiones con un campo propio.

### H. `sitio-prueba/tracker.js` — el "espía"

Este archivo es un pequeño script de JavaScript que se mete en cada página HTML (`index.html`, `productos.html`, `contacto.html`) y hace tres cosas:

1. **Al cargar la página**, abre una sesión si no hay una abierta (`POST /api/sesiones`) y manda el evento "visita" (`POST /api/eventos`).
2. **Cada vez que se da clic en un botón o un link**, manda un evento "clic".
3. **Cada vez que algo pasa**, actualiza la sesión (`PATCH /api/sesiones/<id>`) para renovar su `ultima_actividad`.

```javascript
let visitanteId = localStorage.getItem("visitante_id");
if (!visitanteId) {
  visitanteId = "v-" + Math.random().toString(36).slice(2, 10);
  localStorage.setItem("visitante_id", visitanteId);
}
```
- `localStorage` sobrevive al cierre del navegador: el visitante queda identificado con el mismo UUID aleatorio aunque regrese días después.
- `sessionStorage` solo dura mientras la pestaña esté abierta: por eso lo usamos para la sesión (que debe cerrarse si cierran la pestaña).

**Por diseño nunca guardamos IP, nombre o correo del visitante.** Solo un UUID aleatorio generado en su navegador. Esto respeta el principio de no recopilar datos personales innecesarios.

---

## Parte IV — Manual de operación (comandos)

### Primera vez (instalación)

```powershell
# 1. Levantar las 3 bases en Docker
docker compose up -d

# 2. Instalar las librerías de Python que usa el proyecto
pip install -r requirements.txt

# 3. Arrancar el Web Service
python app.py
```

Abrir el navegador en `http://localhost:5000/api/salud` → las 3 bases deben decir "ok".

### Uso diario

Para arrancar el proyecto después del primer día:
```powershell
docker compose up -d
python app.py
```

Para apagar (al final del día):
- Ctrl+C en la terminal donde está Flask
- `docker compose down` para apagar los contenedores (los datos se mantienen; para borrar todo usa `docker compose down -v`)

### Si `python app.py` da `ModuleNotFoundError: No module named 'flask'`

Pasa cuando estás dentro del venv (`(venv)` en el prompt) pero las librerías están instaladas en el Python general. Dos opciones:

1. **Instalar en el venv:** con el venv activado:
   ```powershell
   pip install -r requirements.txt
   ```
2. **O salir del venv:** `deactivate`, y ya corre `python app.py`.

### Cómo probar un POST en PowerShell

PowerShell tiene un `curl` viejo que no entiende `-H`. Hay 2 formas de evitarlo:

**Opción 1 — Usa `curl.exe` (el curl real de Windows 10+):**
```powershell
curl.exe -X POST http://localhost:5000/api/usuarios -H "Content-Type: application/json" -d "{\"nombre\":\"Ana\",\"email\":\"ana@x.com\"}"
```

**Opción 2 — Script de Python de una línea (lo que usaste tú):**
```powershell
python -c "import urllib.request,json; r=urllib.request.urlopen(urllib.request.Request('http://localhost:5000/api/paginas',data=json.dumps({'sitio_id':1,'ruta':'/productos','titulo':'Productos'}).encode(),headers={'Content-Type':'application/json'},method='POST')); print(r.read().decode())"
```

**Opción 3 (la más cómoda) — Postman:** descargas Postman, creas una colección y haces las pruebas con clics.

---

## Parte V — Flujo de trabajo en Git

### Comandos usados en el día 1 (sábado 15)

```powershell
# Primera vez (crear el repo local y conectarlo al remoto)
git init
git add .
git commit -m "Esqueleto del proyecto y recursos de Angel"
git branch -M main
git remote add origin https://github.com/eliasMG2/T3-01-Proyecto-Multibase-de-datos.git
git push -u origin main

# Siguientes commits
git add .
git commit -m "Sitio de prueba, bitacora y seed"
git push
```

**Qué significa cada comando:**

- `git init` → crea el repositorio local (una carpeta oculta `.git`).
- `git add .` → marca todos los archivos para el próximo commit.
- `git commit -m "mensaje"` → guarda la foto del momento con una etiqueta.
- `git branch -M main` → renombra la rama por defecto de `master` a `main` (convención actual).
- `git remote add origin ...` → conecta el repo local con el repo en GitHub.
- `git push -u origin main` → sube la rama main al remoto.

### Reparto por autor

| Archivo / sección | Autor |
|---|---|
| `docker-compose.yml`, `schema.sql`, `db.py`, `app.py` | Ángel |
| `recursos/usuarios.py`, `recursos/sitios.py`, `recursos/sesiones.py` | Ángel |
| `sitio-prueba/*`, `seed.py`, `README.md`, `docs/*` | Ángel |
| `recursos/paginas.py`, `recursos/objetivos.py`, `recursos/eventos.py` | Elías (los retoma y los hace suyos) |
| Colección de Postman, endpoint de estadísticas | Elías |

Cada quien trabaja en su **rama propia** (`elias-recursos` en el caso de Elías) y abre un Pull Request hacia `main`. Así en la vista de "Contributors" de GitHub se ven los dos nombres con sus commits.

---

## Parte VI — Lo que podría preguntar el profe

El profesor dijo en clase: *"si veo que es código muy avanzado y estructurado, ya sabré que no lo hicieron ustedes"*. Por eso **todo el código está escrito de la forma más sencilla posible**: sin ORM, sin clases raras, con consultas SQL a la vista, con nombres en español, con comentarios explicando el por qué. Si el profe pregunta cualquier cosa de abajo, la respuesta debe estar en el código mismo:

| Pregunta posible | Dónde está la respuesta |
|---|---|
| ¿Dónde está el borrado lógico en MySQL? | Columna `eliminado_en`, filtro `WHERE eliminado_en IS NULL` en cada GET, `UPDATE ... SET eliminado_en = NOW()` en cada DELETE. |
| ¿Dónde está el borrado lógico en MongoDB? | Campo `eliminado: false` en cada documento, filtro `{eliminado: {$ne: true}}`, `$set` en el DELETE. |
| ¿Dónde está el borrado lógico en Redis? | Campo `eliminado = 0` en el hash. `DELETE` lo pone en 1. **No usamos EXPIRE porque borraría físicamente.** |
| ¿Por qué usaron puertos 3307, 27018, 6380? | Para no chocar con los contenedores de MySQL, MongoDB y Redis que ya existen de las prácticas anteriores. |
| ¿Por qué un archivo por recurso? | Para que los dos del equipo podamos trabajar en paralelo sin tocar el mismo archivo y sin generar conflictos al hacer merge. |
| ¿Por qué eventos en MongoDB y no en MySQL? | Porque cada evento tiene campos distintos según su tipo (visita, clic, scroll). En MySQL habría que crear una tabla con columnas llenas de nulos. |
| ¿Por qué el PATCH de eventos solo deja editar `etiquetas` y `revisado`? | Porque un evento es un hecho ocurrido: no se puede "corregir" que alguien visitó la página. Solo se puede clasificar o marcar como revisado. |
| ¿Por qué no usaron un ORM? | Para que el código sea legible y nosotros podamos explicar cada consulta. Un ORM esconde lo que pasa por debajo. |
| ¿Qué pasa si una base se cae? | El endpoint `/api/salud` lo detecta de inmediato. Si cae MongoDB, los endpoints de `/api/eventos` dan error 500; los demás siguen funcionando. |

---

## Parte VII — Declaración de uso de IA

Para este proyecto se utilizó **Claude (Anthropic)** como herramienta de asistencia durante todo el desarrollo. Se empleó para:

1. **Proponer la arquitectura general** (tres motores, repartidos por responsabilidades).
2. **Explicar cómo se implementa el borrado lógico** en cada motor.
3. **Generar el esqueleto del código** (el "molde" del recurso `usuarios.py`), a partir del cual el resto se copió y adaptó.
4. **Guiar paso a paso los comandos** de Docker, pip, git y Python en PowerShell.
5. **Redactar la documentación** (este manual, el README y la bitácora).

Las decisiones de diseño (elección del tema, reparto entre integrantes, puertos distintos para no chocar con prácticas anteriores, decisión de no usar ORM) **se tomaron en acuerdo con el equipo**. Cada archivo entregado fue probado por los alumnos antes de hacer el commit. Los dos integrantes son responsables del contenido final y pueden explicar cada parte del proyecto. El profesor fue claro en clase: *"Pueden guiarse con la IA, no lo hagan todo con la IA"*, y por eso el código se mantuvo intencionalmente simple y los alumnos entienden cada línea.

---

## Parte VIII — Referencias

- **Clases del profesor Francisco Cervantes Zambrano**, Tópicos de Bases de Datos, Instituto Tecnológico de Colima, periodo agosto–diciembre 2026 (transcripciones del 6 de noviembre, planteamiento del proyecto T3-01).
- [1] A. Ronacher, *Flask Documentation*, Pallets Projects. [En línea]. Disponible en: https://flask.palletsprojects.com/
- [2] Oracle Corp., *MySQL 8.0 Reference Manual*. [En línea]. Disponible en: https://dev.mysql.com/doc/refman/8.0/en/
- [3] MongoDB Inc., *MongoDB Manual*. [En línea]. Disponible en: https://www.mongodb.com/docs/manual/
- [4] Redis Ltd., *Redis Documentation*. [En línea]. Disponible en: https://redis.io/docs/latest/
- [5] Docker Inc., *Docker Compose Overview*. [En línea]. Disponible en: https://docs.docker.com/compose/
- [6] R. T. Fielding, *Architectural Styles and the Design of Network-based Software Architectures*, tesis doctoral, Univ. of California Irvine, 2000. (origen del estilo REST).
- [7] M. Massé, *REST API Design Rulebook*. O'Reilly Media, 2011. (buenas prácticas de diseño REST).
