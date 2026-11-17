# Analytics Multibase · Sistema de análisis de visitas web

Proyecto **T3-01** de **Tópicos de Bases de Datos** (Prof. Francisco Cervantes Zambrano), TecNM Campus Colima, agosto–diciembre 2026.

**Equipo:** Ángel Salvador Álvarez Fernández (23460501) · Elías Meléndez Guzmán

Google Analytics simplificado: un sitio de prueba manda las visitas y clics de sus visitantes a este Web Service, que los reparte entre **tres motores de base de datos** y los muestra en un panel visual.

| Motor | Tipo | Qué guarda |
|---|---|---|
| MySQL | Relacional | usuarios, sitios, páginas y objetivos |
| MongoDB | NoSQL documental | eventos de los visitantes (visitas, clics) |
| Redis | Clave-valor | sesiones de visitantes y contadores en vivo |

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.10 o más nuevo](https://www.python.org/downloads/) (en Windows marca *Add Python to PATH*)
- [Git](https://git-scm.com/)

## Instalación y ejecución

```bash
# 1. Clonar
git clone https://github.com/eliasMG2/T3-01-Proyecto-Multibase-de-datos.git
cd T3-01-Proyecto-Multibase-de-datos

# 2. Levantar las 3 bases (MySQL crea las tablas solo con schema.sql)
docker compose up -d

# 3. Instalar librerías
pip install -r requirements.txt

# 4. Arrancar el Web Service
python app.py
```

Abrir en el navegador:

| URL | Qué muestra |
|---|---|
| `http://localhost:5000/` | **Sitio de prueba** (tienda demo que genera visitas y clics) |
| `http://localhost:5000/analiticas` | **Panel visual** con las analíticas (visitas, clics, sesiones, actividad diaria y páginas más vistas) |
| `http://localhost:5000/api/salud` | Estado JSON de las 3 bases |

> MySQL tarda unos 20 segundos en responder la primera vez. Si `/api/salud` marca error en mysql al principio, espera y recarga.

## Verificación con el test suite

Con Flask corriendo, en otra terminal:

```bash
python tests/test_todos_los_endpoints.py
```

Debe terminar con `RESULTADO: 39 OK · 0 FAIL`. El test recorre los 24 endpoints (6 recursos × 4 métodos), verifica el borrado lógico en los 3 motores y comprueba el endpoint de estadísticas que une las tres bases.

## Endpoints del Web Service

El Web Service expone **6 recursos** con sus 4 métodos (24 endpoints) más 3 extras.

### Recursos

| Recurso | Motor | Borrado lógico |
|---|---|---|
| `/api/usuarios` | MySQL | columna `eliminado_en` |
| `/api/sitios` | MySQL | columna `eliminado_en` |
| `/api/paginas` | MySQL | columna `eliminado_en` |
| `/api/objetivos` | MySQL | columna `eliminado_en` |
| `/api/eventos` | MongoDB | campo `eliminado: true` |
| `/api/sesiones` | Redis | campo `eliminado = 1` en hash (sin TTL) |

Cada recurso acepta:

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/<recurso>` | Lista los no borrados |
| GET | `/api/<recurso>/<id>` | Muestra uno |
| POST | `/api/<recurso>` | Crea (JSON en el body) |
| PATCH | `/api/<recurso>/<id>` | Modifica solo los campos enviados |
| DELETE | `/api/<recurso>/<id>` | Borrado lógico |

### Extras

| Ruta | Qué hace |
|---|---|
| `GET /api/salud` | Reporta el estado de las 3 bases |
| `GET /api/estadisticas/<sitio_id>` | Resumen que une MySQL + MongoDB + Redis |
| `GET /analiticas` | Panel visual con gráficas (Jinja + HTML) |

### Ejemplo

```bash
curl -X POST http://localhost:5000/api/usuarios \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Ana\",\"email\":\"ana@correo.com\"}"
```

## Datos de prueba

Para cargar un usuario y un sitio de ejemplo:

```bash
python seed.py
```

Luego abre `http://localhost:5000/` y navega por la tienda demo: cada visita y cada clic se registran automáticamente y se reflejan en el panel de `/analiticas`.

## Estructura del proyecto

```
.
├── app.py                    Web Service (Flask)
├── db.py                     Conexiones a los 3 motores
├── docker-compose.yml        Levanta MySQL, MongoDB y Redis
├── schema.sql                Tablas de MySQL
├── seed.py                   Datos de prueba
├── requirements.txt          Dependencias Python
├── recursos/                 Un archivo por recurso
│   ├── usuarios.py, sitios.py, sesiones.py           (Ángel)
│   ├── paginas.py, objetivos.py, eventos.py          (Elías)
│   ├── estadisticas.py                               (endpoint que une las 3 bases)
│   └── analiticas.py                                 (panel visual)
├── templates/analiticas.html Vista del panel
├── sitio-prueba/             Tienda demo (tracker.js manda eventos)
├── tests/
│   ├── test_todos_los_endpoints.py   Suite completa (39 casos)
│   └── pruebas_elias.py              Casos de Elías
└── docs/
    ├── BITACORA.md                   Bitácora del desarrollo
    ├── MANUAL-LABORATORIO.md         Manual técnico completo
    └── 23460501 - T3-01 Manual de Laboratorio Multibase.pdf
```

## Detener

```bash
docker compose down
```

## Integrantes y autoría

- **Ángel Salvador Álvarez Fernández (23460501)** · esqueleto del proyecto (`docker-compose.yml`, `schema.sql`, `db.py`, `app.py`), recursos `usuarios`, `sitios` (MySQL) y `sesiones` (Redis), sitio de prueba con `tracker.js`, suite de pruebas, endpoint `/api/estadisticas`, bitácora y manual de laboratorio.
- **Elías Meléndez Guzmán** · recursos `paginas`, `objetivos` (MySQL) y `eventos` (MongoDB), **panel visual `/analiticas`** con gráficas y filtros, corrección de autenticación MySQL, integración del redirect desde `/`.
