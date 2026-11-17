# Manual de Laboratorio — Proyecto Multibase T3-01

**Materia:** Tópicos de Bases de Datos (IFF-1026) · 3° Unidad
**Profesor:** Francisco Cervantes Zambrano · Instituto Tecnológico de Colima
**Alumnos:** Ángel Salvador Álvarez Fernández (23460501) · Elías Meléndez Guzmán
**Entrega:** martes 17 de noviembre de 2026

Este documento explica **todo** el proyecto paso a paso: para qué sirve cada archivo, qué significa cada línea de código importante, qué comandos se usaron y por qué. Está escrito para que cualquiera del equipo pueda abrirlo, leerlo y defender el trabajo frente al profesor.

---

## Parte I — Conceptos base

### 1. ¿Qué es un sistema multibase de datos?

En clase (transcripción del 6 de noviembre) el profesor lo explicó así: *"Se refiere a aquellos sistemas que no solo utilizan una base de datos, sino que utilizan múltiples motores de base de datos para resolver problemas. Cada motor tiene un propósito distinto"*.

La idea es que, en lugar de forzar a un solo motor a hacerlo todo, se usan **varios motores especializados**:

- **MySQL** — relacional, bueno para datos estructurados, relaciones, transacciones.
- **MongoDB** — NoSQL documental, bueno para datos con forma variable.
- **Redis** — clave-valor en memoria, bueno para lecturas y escrituras ultra rápidas.

En nuestro proyecto cada motor guarda lo que mejor sabe guardar.

### 2. ¿Qué es un Web Service?

Es un programa que corre en un servidor y **responde por HTTP**. En lugar de devolver HTML para una persona, devuelve **datos en JSON** para que los use otro programa o un panel visual.

Nuestro Web Service es `app.py`. Se arranca con `python app.py` y queda escuchando en el puerto 5000. Se le hacen peticiones a URLs como `http://localhost:5000/api/usuarios` y responde con JSON.

### 3. ¿Qué son GET, POST, PATCH y DELETE?

Son los **verbos HTTP**. Cada uno es una acción distinta sobre un recurso:

- **GET** — leer o consultar. Ejemplo: "dame la lista de usuarios".
- **POST** — crear. Ejemplo: "crea un nuevo usuario con estos datos".
- **PATCH** — modificar parcialmente. Ejemplo: "cambia solo el rol del usuario 1".
- **DELETE** — borrar. Ejemplo: "borra el usuario 1".

Juntos forman una **API REST**. El profesor pidió que los 6 recursos tengan los 4 métodos, lo que da **6 × 4 = 24 endpoints** en total.

### 4. ¿Qué es un "recurso"?

Cuando preguntaron qué era un recurso, el profesor contestó: *"Si usted tiene usuarios, artículos, ventas, categorías, proveedores, sucursales, cada uno de esos es un recurso y cada uno va a tener su propio GET, POST, PATCH y DELETE"*.

Un recurso es básicamente **un tipo de cosa** que la aplicación maneja. En nuestro caso: usuarios, sitios, páginas, objetivos, eventos y sesiones.

### 5. ¿Qué es el "borrado lógico"?

Cuando el profesor dijo *"el borrado de los registros deberá ser lógico, no se elimina el registro, sólo se marca como borrado"*, se refiere a esto:

- **Borrado físico (lo normal):** el registro se elimina de la base y se pierde para siempre.
- **Borrado lógico (lo que pide):** el registro se queda en la base, pero se le añade una marca que dice "está borrado". Las consultas normales lo ignoran, pero el dato sigue ahí.

Es como tachar un nombre con lápiz en vez de arrancar la hoja. Ventaja: nunca se pierde información y se puede auditar quién borró qué.

### 6. ¿Qué es Docker y por qué lo usamos?

Docker es un programa que permite correr aplicaciones (como MySQL, MongoDB o Redis) **dentro de contenedores aislados**, sin instalarlas directamente en la computadora. Cada contenedor es como una mini-computadora virtual con una sola aplicación.

En nuestro proyecto, en vez de instalar MySQL, MongoDB y Redis en Windows (cada uno con sus propios conflictos), levantamos los tres de un jalón con `docker-compose.yml`, y cuando terminamos los apagamos con un solo comando.

El profesor ya lo usó en el tema 1.

---

## Parte II — Arquitectura del proyecto

La aplicación tiene tres capas conectadas por HTTP y los tres motores viviendo en contenedores Docker.

- **Capa 1 — Cliente:** el navegador. Puede entrar al sitio de prueba (genera eventos) o al panel de analíticas (ve los resultados).
- **Capa 2 — Web Service (Flask):** recibe peticiones HTTP, llama a los motores correspondientes y devuelve JSON o la vista HTML del panel.
- **Capa 3 — Motores:** MySQL guarda lo administrativo; MongoDB guarda los eventos; Redis guarda las sesiones.

Flujo típico cuando un visitante entra a `/productos` en el sitio de prueba:

1. El navegador carga `productos.html` y con él el script `tracker.js`.
2. `tracker.js` abre una sesión con `POST /api/sesiones` (se guarda en **Redis**).
3. `tracker.js` dispara `POST /api/eventos` con el evento "visita" (se guarda en **MongoDB**).
4. Si el visitante da clic, otro `POST /api/eventos` con el evento "clic".
5. Al entrar a `/analiticas`, Flask consulta las 3 bases y arma el panel con las gráficas.

---

## Parte III — Archivo por archivo

### A. `docker-compose.yml` — las 3 bases en contenedores

Define 3 servicios: `mysql`, `mongo` y `redis`, cada uno con su imagen oficial. Puntos clave:

- `container_name: analytics-...` → nombre que verás en Docker Desktop; les pusimos "analytics-*" para distinguirlos de contenedores de prácticas pasadas.
- `ports: "3307:3306"` → el puerto 3306 del contenedor se asoma al 3307 de la computadora. **Usamos 3307, 27018 y 6380 (no los puertos normales)** para no chocar con los contenedores de MySQL, MongoDB y Redis que ya existen de prácticas anteriores.
- `volumes: ./schema.sql:/docker-entrypoint-initdb.d/schema.sql` → hace que MySQL ejecute `schema.sql` al arrancar por primera vez y cree las tablas automáticamente.

### B. `schema.sql` — las 4 tablas de MySQL

Crea la base `analytics` y 4 tablas: `usuarios`, `sitios`, `paginas` y `objetivos`.

Lo clave: cada tabla tiene una columna **`eliminado_en DATETIME NULL`**. Mientras esté en `NULL`, el registro está vivo. Cuando le ponemos la fecha, queda borrado lógicamente.

### C. `db.py` — las 3 conexiones

Define cómo Python se conecta a cada motor.

- `conectar_mysql()` es una función que abre y regresa una conexión fresca. Usamos `DictCursor` para que los resultados vengan como diccionarios en vez de tuplas, y `autocommit=True` para no tener que llamar `commit()`.
- `cliente_mongo = MongoClient(...)` es una variable global (MongoDB puede compartir un solo cliente para toda la app).
- `r = redis.Redis(..., decode_responses=True)` para que Redis devuelva texto en vez de bytes.

### D. `app.py` — el Web Service

Importa Flask, carga los 8 blueprints (6 recursos + estadisticas + analiticas), expone `/api/salud` y arranca el servidor en el puerto 5000. También incluye `GET /` que redirige al sitio de prueba.

Los **Blueprints** son mini-apps que se enchufan al Flask principal. Cada recurso vive en su propio archivo con su Blueprint. Ventaja práctica: Ángel y Elías pueden editar sus archivos sin tocar el mismo fichero y sin generar conflictos al hacer merge.

### E. `recursos/usuarios.py` — el molde CRUD

El archivo más importante de entender, porque los otros 3 recursos de MySQL (sitios, paginas, objetivos) son copias de este con el nombre de la tabla cambiado.

**GET lista:** `SELECT * FROM usuarios WHERE eliminado_en IS NULL`. El filtro ignora los borrados.

**POST:** valida que el body traiga nombre y email, hace `INSERT` con parámetros `%s` (nunca concatenamos strings, para evitar inyección SQL).

**PATCH:** solo acepta los campos listados en `CAMPOS_EDITABLES` (lista blanca). Arma el UPDATE dinámicamente con los campos que mandó el cliente.

**DELETE:** NO es un `DELETE FROM`. Es un `UPDATE usuarios SET eliminado_en = NOW()`. Ese es exactamente el borrado lógico que pide el profesor.

### F. `recursos/eventos.py` — MongoDB

MongoDB no usa SQL ni cursores. Usa métodos como `insert_one`, `find`, `update_one`.

Cada evento es un documento JSON. **MongoDB permite que los documentos tengan campos distintos** (un evento "visita" lleva `ruta`, uno "clic" lleva `selector` y `texto`), y esa flexibilidad es la razón por la que los eventos viven en MongoDB y no en MySQL.

**Regla especial del PATCH:** solo deja cambiar `etiquetas` y `revisado`. Un evento es un hecho ocurrido: no se puede "corregir" que alguien visitó la página, solo clasificarlo o marcarlo como revisado.

**DELETE:** `update_one` con `$set: {eliminado: true}`. Nunca `delete_one`.

### G. `recursos/sesiones.py` — Redis

Una sesión vive como un HASH con clave `sesion:{id}`. Además se mete al sorted set `sitio:{id}:activas` para poder contar las sesiones activas con una sola consulta.

**IMPORTANTE — el borrado lógico en Redis es el más delicado:** NO usamos `DEL`, solo cambiamos el campo `eliminado` del hash a 1. Y **no le ponemos TTL (EXPIRE)**: si lo hiciéramos, Redis borraría físicamente la sesión cuando caducara y rompería el requisito del profesor.

### H. `recursos/estadisticas.py` — endpoint que une las 3 bases

`GET /api/estadisticas/<sitio_id>` responde con un JSON como:

```json
{
  "sitio_id": 1,
  "sitio_nombre": "Mi Tienda",
  "total_eventos": 42,
  "sesiones_activas": 3
}
```

Consulta MySQL (nombre del sitio), MongoDB (total de eventos no borrados) y Redis (sesiones activas en el sorted set) **en el mismo endpoint**.

### I. `recursos/analiticas.py` y `templates/analiticas.html` — el panel visual

El endpoint `/analiticas` renderiza una página HTML con filtro por sitio y las siguientes secciones:

- Tarjetas con los totales (Visitas, Clics, Sesiones).
- Gráfica de actividad diaria de los últimos 7 días.
- Lista de páginas más visitadas.
- Bitácora con los últimos eventos registrados en cada motor.

La consulta a MongoDB usa una sola agregación con `$facet` para traer en una pasada: totales por tipo, actividad por día, top páginas y eventos recientes. Es mucho más eficiente que hacer 4 consultas separadas.

### J. `sitio-prueba/tracker.js` — el espía

Un pequeño script de JavaScript que se mete en cada página HTML del sitio de prueba. Hace tres cosas:

1. **Al cargar la página:** abre una sesión (si no existe) y manda el evento "visita".
2. **Al hacer clic en un botón o link:** manda un evento "clic".
3. **Cada vez que hay actividad:** actualiza la sesión (PATCH) para renovar `ultima_actividad`.

Usamos `localStorage` para el `visitante_id` (persiste entre sesiones del navegador) y `sessionStorage` para el `sesion_id` (dura mientras la pestaña esté abierta). **No guardamos IP, nombre ni correo del visitante** — solo un UUID aleatorio generado en su navegador, respetando el principio de no recopilar datos personales innecesarios.

---

## Parte IV — Manual de operación

### Primera vez (instalación)

```powershell
# 1. Levantar las 3 bases en Docker
docker compose up -d

# 2. Instalar librerías
pip install -r requirements.txt

# 3. Arrancar el Web Service
python app.py
```

Abrir en el navegador:

- `http://localhost:5000/api/salud` → debe decir las 3 bases en "ok".
- `http://localhost:5000/` → se abre el sitio de prueba (tienda demo).
- `http://localhost:5000/analiticas` → se abre el panel visual.

### Verificar con el test suite

Con Flask corriendo, en otra terminal:

```powershell
python tests/test_todos_los_endpoints.py
```

Debe terminar con `RESULTADO: 39 OK · 0 FAIL`.

### Cargar datos de prueba

```powershell
python seed.py
```

Mete un usuario y un sitio de ejemplo para poder probar los demás endpoints.

### Detener

- `Ctrl+C` en la terminal de Flask.
- `docker compose down` para apagar los contenedores (los datos se conservan hasta `docker compose down -v`).

### Soluciones a errores comunes

- **`ModuleNotFoundError: No module named 'flask'`** → estás dentro del venv pero sin librerías. Con el venv activado: `pip install -r requirements.txt`.
- **`WinError 10061` o "connection refused"** → Docker Desktop no está encendido o los contenedores están apagados. Abre Docker Desktop y espera a que diga "Engine running"; luego `docker compose up -d`.
- **404 al entrar a `http://localhost:5000/`** → esto solo pasa si no hiciste `git pull` para traer el redirect. Después del pull, `/` redirige al sitio de prueba automáticamente.
- **`curl` falla en PowerShell** → PowerShell tiene un alias viejo de curl. Usa `curl.exe` con el `.exe` explícito, o usa el `seed.py` / un script de Python.

---

## Parte V — Flujo de Git

Cada quien trabaja en su rama y sube con su propia cuenta de GitHub para que los commits aparezcan a su nombre. Comandos usados:

```powershell
git init                          # crea el repo local
git add .                         # marca los archivos a commit
git commit -m "mensaje"           # guarda la foto del momento
git branch -M main                # usa main como rama por defecto
git remote add origin <url>       # conecta con GitHub
git push -u origin main           # sube la rama

git pull --rebase                 # trae lo del compañero sin crear "merge commits"
git tag -a v1.0-entrega -m "..."  # crea un tag
git push origin v1.0-entrega      # sube el tag
```

Reparto por autor:

- **Ángel (4 commits + aportes):** `docker-compose.yml`, `schema.sql`, `db.py`, `app.py`, recursos `usuarios/sitios/sesiones`, sitio de prueba, suite de pruebas, endpoint `estadisticas`, bitácora y manual.
- **Elías (3 commits incluyendo un Pull Request):** recursos `paginas/objetivos/eventos`, panel `/analiticas`, corrección de autenticación MySQL, redirect de `/`.

---

## Parte VI — Lo que podría preguntar el profe

| Pregunta | Dónde está la respuesta |
|---|---|
| ¿Dónde está el borrado lógico en MySQL? | Columna `eliminado_en`, filtro `WHERE eliminado_en IS NULL` en cada GET, `UPDATE ... SET eliminado_en = NOW()` en cada DELETE. |
| ¿Dónde está el borrado lógico en MongoDB? | Campo `eliminado`. Filtro `{eliminado: {$ne: true}}`. `$set` en el DELETE. |
| ¿Dónde está el borrado lógico en Redis? | Campo `eliminado = 0` en el hash. **No usamos EXPIRE/TTL** porque borraría físicamente. |
| ¿Por qué usaron puertos 3307, 27018, 6380? | Para no chocar con los contenedores de prácticas anteriores. |
| ¿Por qué un archivo por recurso? | Para que los dos del equipo trabajemos en paralelo sin conflictos. |
| ¿Por qué eventos en MongoDB y no en MySQL? | Porque cada evento tiene campos distintos según su tipo. |
| ¿Por qué el PATCH de eventos solo deja editar `etiquetas` y `revisado`? | Porque un evento es un hecho ocurrido: no se puede "corregir". |
| ¿Por qué no usaron un ORM? | Para que podamos explicar cada consulta y que el código sea legible. |
| ¿Cómo se demuestra que los 24 endpoints funcionan? | Con `python tests/test_todos_los_endpoints.py`, que pasa 39 OK. |
| ¿Qué hace el endpoint `/api/estadisticas`? | Devuelve un JSON que combina datos de los 3 motores en una sola respuesta. |
| ¿Qué hace `/analiticas`? | Devuelve un panel HTML con gráficas, usando una agregación de MongoDB con `$facet`. |

---

## Parte VII — Declaración de uso de IA

Para este proyecto se utilizó **Claude (Anthropic)** como herramienta de guía: para organizar la estructura, explicar cómo implementar el borrado lógico en cada motor, generar el esqueleto del código y redactar la documentación. Cada archivo fue probado por los alumnos antes del commit. Los dos integrantes son responsables del contenido final y pueden explicar cada parte del proyecto. El profesor fue claro en clase: *"Pueden guiarse con la IA, no lo hagan todo con la IA"*, y por eso el código se mantuvo intencionalmente simple y los alumnos entienden cada línea.

## Parte VIII — Referencias

- Clases del profesor Francisco Cervantes Zambrano, Tópicos de Bases de Datos, Instituto Tecnológico de Colima, periodo agosto–diciembre 2026.
- A. Ronacher, *Flask Documentation*. https://flask.palletsprojects.com/
- Oracle Corp., *MySQL 8.0 Reference Manual*. https://dev.mysql.com/doc/refman/8.0/en/
- MongoDB Inc., *MongoDB Manual*. https://www.mongodb.com/docs/manual/
- Redis Ltd., *Redis Documentation*. https://redis.io/docs/latest/
- Docker Inc., *Docker Compose Overview*. https://docs.docker.com/compose/
- R. T. Fielding, *Architectural Styles and the Design of Network-based Software Architectures*, tesis doctoral, Univ. of California Irvine, 2000 (origen del estilo REST).
