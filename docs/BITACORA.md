# Bitácora de laboratorio — Proyecto Multibase T3-01

**Materia:** Tópicos de Bases de Datos (IFF-1026)
**Profesor:** Francisco Cervantes Zambrano
**Alumnos:** Ángel Salvador Álvarez Fernández (23460501) · Elías Meléndez Guzmán
**Periodo:** agosto–diciembre 2026

Este documento registra paso a paso cómo se desarrolló el proyecto.

## 1. Planteamiento

El profesor pidió elaborar una aplicación multibase de datos que conecte al menos **tres motores** (uno relacional, uno NoSQL y uno clave-valor), expuesta como un **Web Service** con los métodos GET, POST, PATCH y DELETE en **al menos seis recursos**. El **borrado debe ser lógico**. La entrega es por **repositorio Git compartido** con README y commits de los dos integrantes.

### Tema elegido
Sistema de análisis de visitas web (Google Analytics simplificado). Cada motor tiene una responsabilidad natural y distinta:

- **MySQL** guarda lo administrativo y estructurado (usuarios, sitios, páginas, objetivos).
- **MongoDB** guarda los eventos de los visitantes (visitas, clics), cuyos atributos cambian según el tipo.
- **Redis** mantiene las sesiones activas y los contadores en vivo.

## 2. Arquitectura

El sitio de prueba manda eventos al Web Service con `fetch`. El Web Service los reparte entre MySQL, MongoDB y Redis. El panel de analíticas los lee y los muestra en gráficas.

```
Navegador                       Flask (app.py)
┌────────────────┐    JSON     ┌──────────────────────────┐
│ sitio-prueba/  │  ────────►  │  /api/* (24 endpoints)   │
│ tracker.js     │             │  /api/salud              │
│ (visita, clic) │             │  /api/estadisticas/<id>  │
└────────────────┘             │  /analiticas (panel)     │
                               └──┬──────────┬──────────┬─┘
                                  ▼          ▼          ▼
                               MySQL     MongoDB     Redis
                               :3307     :27018      :6380
```

Los tres motores corren en **contenedores Docker** orquestados con `docker-compose`. El Web Service está en Python + Flask.

## 3. Reparto de trabajo

| Recurso / aporte | Motor | Responsable |
|---|---|---|
| `usuarios` | MySQL | Ángel |
| `sitios` | MySQL | Ángel |
| `sesiones` | Redis | Ángel |
| `paginas` | MySQL | Elías |
| `objetivos` | MySQL | Elías |
| `eventos` | MongoDB | Elías |
| Esqueleto, docker-compose, suite de pruebas, `estadisticas`, bitácora | — | Ángel |
| Panel `/analiticas` con gráficas, corrección de autenticación MySQL, redirect de `/` | — | Elías |

## 4. Borrado lógico en los 3 motores

Es el requisito que exige una solución distinta en cada motor:

- **MySQL:** se añade la columna `eliminado_en DATETIME NULL` en cada tabla. `DELETE` ejecuta `UPDATE ... SET eliminado_en = NOW()`. Los `GET` filtran con `WHERE eliminado_en IS NULL`.
- **MongoDB:** cada documento lleva un campo `eliminado: false`. `DELETE` lo pone en `true`. Los `GET` filtran con `{eliminado: {$ne: true}}`.
- **Redis:** cada sesión es un `HASH` con un campo `eliminado = 0`. `DELETE` lo cambia a `1` y hace `ZREM` del sorted set de sesiones activas. **No se usa EXPIRE/TTL**, porque si Redis venciera el TTL eliminaría físicamente la sesión y rompería el requisito.

## 5. Decisiones técnicas

- **Puertos 3307, 27018, 6380** en Docker para no chocar con los contenedores de las prácticas pasadas.
- **Blueprints de Flask**, un archivo por recurso, para que ambos integrantes trabajen en paralelo sin conflictos de merge.
- **PyMySQL** en vez de mysql-connector, por simplicidad.
- **Sin ORM** a propósito: el profesor advirtió que un código demasiado estructurado haría sospechar que no lo hicimos nosotros. Las consultas se escriben a mano para poder explicar cada línea.

## 6. Avances cronológicos

### Sábado 15 de noviembre
- Elección del tema y reparto con Elías por WhatsApp.
- Esqueleto: `docker-compose.yml`, `schema.sql`, `db.py`, `app.py` con `/api/salud`, recurso `usuarios` como molde.
- Recursos `sitios` y `sesiones`.
- Sitio de prueba (3 páginas HTML + `tracker.js`) y `seed.py`.
- Stubs de los recursos de Elías (`paginas.py`, `objetivos.py`, `eventos.py`) como punto de partida.
- Suite de pruebas `test_todos_los_endpoints.py` y endpoint extra `/api/estadisticas`.
- Primer push al repositorio con 4 commits.

### Domingo 16 de noviembre — reposo
### Lunes 16 de noviembre — reposo

### Martes 17 de noviembre (día de entrega)
- `git pull --rebase` para traer los cambios de Elías.
- Elías subió su parte con un **Pull Request** (lo más profesional en GitHub):
  - Corrección de autenticación MySQL.
  - **Panel de analíticas en `/analiticas`** (`recursos/analiticas.py`, `templates/analiticas.html`, `sitio-prueba/analiticas.css`) con filtros por sitio, visitas, clics, sesiones, actividad diaria y páginas más vistas.
  - Redirect desde `/` al sitio de prueba.
  - Funciones auxiliares `sitios_registrados()` y `sesiones_registradas()` para reutilizar lógica entre recursos.
- Verificación: suite de pruebas pasa **39 OK · 0 FAIL**.
- Prueba desde cero clonando en `prueba-limpia`: **39 OK · 0 FAIL**. El proyecto es reproducible.
- Limpieza de notas personales del repositorio.
- Actualización de README, bitácora y manual de laboratorio.
- Tag `v1.0-entrega` creado y empujado.
- Entrega en Classroom antes de las 11:00.

## 7. Resultado final

El proyecto cumple y supera los requisitos:

| Requisito | Estado |
|---|---|
| 3 motores (relacional, NoSQL, clave-valor) | MySQL, MongoDB, Redis |
| Web Service con GET/POST/PATCH/DELETE en los 6 recursos | 24 endpoints, los 39 casos pasan |
| Borrado lógico en los 3 motores | Verificado con el test |
| 6 recursos distintos | Sí (usuarios, sitios, páginas, objetivos, eventos, sesiones) |
| Repositorio Git con commits de los dos integrantes | Sí (Ángel y Elías, incluye un Pull Request) |
| README con instrucciones | Sí, actualizado |

Extras entregados sobre lo pedido: endpoint `/api/estadisticas` que une las 3 bases, panel visual `/analiticas` con gráficas, sitio de prueba con tracker JavaScript, suite de pruebas automatizada, manual de laboratorio en PDF.

## 8. Declaración de uso de IA

Para este proyecto se utilizó **Claude (Anthropic)** como herramienta de guía: para proponer la arquitectura, para explicar cómo implementar el borrado lógico en cada motor, para generar el esqueleto del código y para redactar la documentación. Cada archivo fue probado por los alumnos antes de hacer commit. Los dos integrantes son responsables del contenido final y pueden explicar cada parte del proyecto.
