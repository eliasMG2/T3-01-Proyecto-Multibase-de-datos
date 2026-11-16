# Bitácora de laboratorio — Proyecto Multibase T3-01

**Materia:** Tópicos de Bases de Datos (IFF-1026)
**Profesor:** Francisco Cervantes Zambrano
**Alumnos:** Ángel Salvador Álvarez Fernández (23460501), Elías Meléndez Guzmán
**Periodo:** agosto–diciembre 2026

Este documento registra paso a paso cómo se desarrolló el proyecto. Sirve como respaldo en caso de que el profesor pida sustentar lo hecho, y como manual del laboratorio.

---

## 1. Planteamiento

El profesor pidió elaborar una aplicación multibase de datos que conecte con al menos **tres motores** (uno relacional, uno NoSQL y uno clave-valor), expuesta como un **Web Service** con los métodos GET, POST, PATCH y DELETE en **al menos seis recursos**. El **borrado debe ser lógico** (el registro no se elimina, solo se marca). La entrega es por **repositorio Git compartido** con README y commits de todos los integrantes.

### Tema elegido
Sistema de análisis de visitas web (un Google Analytics simplificado). Se eligió porque los tres motores tienen una responsabilidad natural y distinta:
- **MySQL** guarda lo administrativo y estructurado (usuarios, sitios, páginas, objetivos).
- **MongoDB** guarda los eventos de los visitantes (visitas, clics, scroll), cuyos atributos cambian según el tipo.
- **Redis** mantiene las sesiones activas y contadores en vivo, donde interesa la velocidad por encima de la persistencia estricta.

---

## 2. Arquitectura

```
+------------------+        +-------------------------+        +-----------+
|  Sitio de prueba |  JSON  |   Web Service (Flask)   |        |  MySQL    |  <- usuarios, sitios,
|  (HTML + JS)     | -----> |  app.py + /api/*        | -----> |           |     paginas, objetivos
+------------------+        |  blueprints por recurso | -----> +-----------+
                            |                         |        +-----------+
                            |                         | -----> |  MongoDB  |  <- eventos
                            |                         |        +-----------+
                            |                         |        +-----------+
                            |                         | -----> |   Redis   |  <- sesiones,
                            +-------------------------+        +-----------+     contadores
```

Los tres motores corren en **contenedores Docker**, orquestados con `docker-compose`. El Web Service está en Python + Flask (el mismo stack que el profesor usó en la clase de Docker del tema 1).

---

## 3. Reparto de trabajo

| Recurso | Motor | Responsable |
|---|---|---|
| `usuarios` | MySQL | Ángel |
| `sitios` | MySQL | Ángel |
| `sesiones` | Redis | Ángel |
| `paginas` | MySQL | Elías |
| `objetivos` | MySQL | Elías |
| `eventos` | MongoDB | Elías |

Además, Ángel preparó el esqueleto del proyecto, `docker-compose.yml`, el sitio de prueba y el README. Elías preparará la colección de Postman y el panel simple.

---

## 4. Diseño: el borrado lógico en los tres motores

Es el único requisito del profesor que exige una solución distinta en cada motor:

- **MySQL:** se añade la columna `eliminado_en DATETIME NULL` en cada tabla. `DELETE` ejecuta `UPDATE ... SET eliminado_en = NOW()`. Los `GET` filtran con `WHERE eliminado_en IS NULL`.
- **MongoDB:** cada documento lleva un campo `eliminado: false`. `DELETE` lo pone en `true`. Los `GET` filtran con `{eliminado: {$ne: true}}`.
- **Redis:** cada sesión es un `HASH` con un campo `eliminado = 0`. `DELETE` lo cambia a `1` y hace `ZREM` del sorted set de sesiones activas. **Importante:** no se usa `EXPIRE`/TTL, porque si Redis vence el TTL eliminaría físicamente la sesión y rompería el requisito.

---

## 5. Decisiones técnicas registradas

- **Puertos distintos en Docker (3307, 27018, 6380)** para no chocar con los contenedores de MySQL, MongoDB y Redis que ya existen de prácticas anteriores.
- **Blueprints de Flask** (un archivo por recurso en `recursos/`) para que cada compañero trabaje su recurso sin tocar los demás y sin generar conflictos al hacer merge.
- **PyMySQL en vez de mysql-connector** porque es más sencillo y suficiente para el proyecto.
- **No se usa un ORM** (ni SQLAlchemy ni Mongoose) a propósito: el profesor advirtió que si ve código demasiado estructurado sabrá que no lo hicimos nosotros. Las consultas se escriben a mano para que podamos explicarlas.

---

## 6. Avances cronológicos

### Sábado 15 de noviembre (día 1)
- Se eligió el tema y se acordó por WhatsApp el reparto con Elías.
- Ángel creó el esqueleto: `docker-compose.yml`, `schema.sql`, `db.py` con las tres conexiones, `app.py` con `/api/salud`, y el primer recurso `usuarios` como molde.
- Se probó local: las tres bases respondieron `ok` en `/api/salud`. El CRUD completo de usuarios funcionó (POST, GET, PATCH, DELETE lógico).
- Se añadieron los recursos `sitios` (MySQL) y `sesiones` (Redis).
- Se creó el sitio de prueba (3 páginas HTML + `tracker.js`) que simula las visitas y clics.
- Primer commit y push al repositorio `eliasMG2/T3-01-Proyecto-Multibase-de-datos`.

### Domingo 16 de noviembre (día 2) — pendiente
- Elías: implementa `paginas`, `objetivos` y `eventos`.
- Ángel: integra y prueba el sitio de prueba de punta a punta.
- Reunión 12 pm: integración conjunta en llamada.

### Lunes 17 de noviembre (día 3, entrega) — pendiente
- Pruebas finales, README completo, colección Postman, tag `v1.0-entrega`.

---

## 7. Declaración de uso de IA

Para este proyecto se utilizó Claude (Anthropic) como herramienta de guía: para proponer la arquitectura, para explicar cómo se implementa el borrado lógico en cada motor, y para generar el esqueleto del código a partir del cual cada integrante del equipo escribió sus recursos. Cada archivo entregado fue revisado, probado y, cuando fue necesario, modificado por los alumnos; los dos integrantes son responsables del contenido final.

### Actualización — sábado 15, noche

Para asegurar que Elías no empiece de cero y pueda avanzar rápido mañana:
- Se añadieron los stubs (archivos pre-hechos a partir del molde `usuarios.py`) de sus tres recursos: `paginas.py`, `objetivos.py` y `eventos.py` (este último en MongoDB con la restricción de PATCH solo a `etiquetas` y `revisado`).
- Se actualizó `app.py` registrando los 6 blueprints.
- Se añadió `PARA-ELIAS.md` con instrucciones de cómo clonar, arrancar, probar sus recursos y hacer sus propios aportes (colección Postman, endpoint de estadísticas).

Con esto, al final del sábado el proyecto ya tiene **los 6 recursos funcionales**. Elías debe probarlos, personalizarlos y añadir sus aportes propios en su rama `elias-recursos`.
