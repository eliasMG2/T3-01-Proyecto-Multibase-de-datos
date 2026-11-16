# Analytics Multibase — Sistema de análisis de visitas web

Proyecto T3-01 de **Tópicos de Bases de Datos** (Prof. Francisco Cervantes Zambrano), TecNM Campus Colima, agosto–diciembre 2026.

**Equipo:** Ángel Salvador Álvarez Fernández · Elías Meléndez Guzmán

Es un Google Analytics simplificado: un sitio de prueba manda las visitas y clics de sus visitantes a este Web Service, y el Web Service los guarda repartidos en **tres motores de base de datos**:

| Motor | Tipo | Qué guarda |
|---|---|---|
| MySQL | Relacional | usuarios, sitios, páginas y objetivos |
| MongoDB | NoSQL (documentos) | eventos de los visitantes (visitas, clics, scroll) |
| Redis | Clave-valor | sesiones de visitantes y contadores en vivo |

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (abierto y corriendo)
- [Python 3.10 o más nuevo](https://www.python.org/downloads/) (en Windows marcar *Add Python to PATH*)
- [Git](https://git-scm.com/)
- Postman (opcional, para probar)

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/USUARIO/analytics-multibase.git
cd analytics-multibase

# 2. Levantar las 3 bases de datos (MySQL crea las tablas solo con schema.sql)
docker compose up -d

# 3. Crear un entorno virtual e instalar las librerías
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / Mac
pip install -r requirements.txt
```

## Ejecución

```bash
python app.py
```

El Web Service queda en `http://localhost:5000`. Para comprobar que se conectó a las tres bases, abre en el navegador:

```
http://localhost:5000/api/salud
```

Debe responder `{"mongodb": "ok", "mysql": "ok", "redis": "ok"}`.

> La primera vez MySQL tarda unos 20 segundos en arrancar. Si `/api/salud` marca error en mysql, espera un poco y recarga.

## Recursos del Web Service

Cada recurso tiene los cuatro métodos. El **DELETE es borrado lógico**: el registro no se elimina, solo se marca como borrado y deja de aparecer en los GET.

| Recurso | Motor | Cómo se marca el borrado |
|---|---|---|
| `/api/usuarios` | MySQL | columna `eliminado_en` con la fecha |
| `/api/sitios` | MySQL | columna `eliminado_en` |
| `/api/paginas` | MySQL | columna `eliminado_en` |
| `/api/objetivos` | MySQL | columna `eliminado_en` |
| `/api/eventos` | MongoDB | campo `eliminado: true` |
| `/api/sesiones` | Redis | campo `eliminado` = 1 en el hash de la sesión |

Métodos de cada recurso:

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/<recurso>` | Lista los registros no borrados |
| GET | `/api/<recurso>/<id>` | Muestra uno |
| POST | `/api/<recurso>` | Crea uno (datos en JSON) |
| PATCH | `/api/<recurso>/<id>` | Modifica solo los campos enviados |
| DELETE | `/api/<recurso>/<id>` | Borrado lógico |

Ejemplo:

```bash
curl -X POST http://localhost:5000/api/usuarios -H "Content-Type: application/json" -d "{\"nombre\": \"Ana\", \"email\": \"ana@correo.com\"}"
```

## Detener

```bash
docker compose down
```
