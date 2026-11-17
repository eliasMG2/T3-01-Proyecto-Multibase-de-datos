# ELÍAS — LEE ESTO. Entregas HOY martes 17 nov antes de 11:59

Vamos a hacer que tengas **3 commits reales** desde tu cuenta de GitHub, en menos de 1 hora, sin riesgo de romper nada. Todo es **copiar y pegar** en orden.

---

## 0. Lo que debes tener instalado (verifica)

Abre PowerShell y pega esto uno por uno. Si falla alguno, instala lo que falte:

```powershell
git --version
python --version
docker --version
```

- **Git:** https://git-scm.com/download/win
- **Python 3.10+:** https://www.python.org/downloads/ (al instalar marca ✅ *Add Python to PATH*)
- **Docker Desktop:** https://www.docker.com/products/docker-desktop/

Después de instalar, **cierra y vuelve a abrir** PowerShell. Y abre Docker Desktop (icono de la ballena en la bandeja).

---

## 1. Clonar el repo y entrar

Abre PowerShell y pega:

```powershell
cd $env:USERPROFILE\Documents
git clone https://github.com/eliasMG2/T3-01-Proyecto-Multibase-de-datos.git
cd T3-01-Proyecto-Multibase-de-datos
```

## 2. Configurar git con TU cuenta (una vez)

```powershell
git config user.name "eliasMG2"
git config user.email "TUCORREODEGITHUB@ejemplo.com"
```

> Cambia **TUCORREODEGITHUB** por el email que tienes en tu cuenta de GitHub. Es **crítico** que sea el mismo para que tus commits aparezcan con tu foto en el repo.

## 3. Levantar las 3 bases y arrancar la API

```powershell
docker compose up -d
pip install -r requirements.txt
python app.py
```

Abre `http://localhost:5000/api/salud` en el navegador → debe decir `{"mysql":"ok","mongodb":"ok","redis":"ok"}`.

**Deja esta terminal corriendo** con Flask.

---

## COMMIT 1 — Mi endpoint de estadísticas (aporte propio)

Abre **otra terminal** de PowerShell en la misma carpeta (botón + arriba o `Ctrl+Shift+ñ`). El archivo `recursos/estadisticas.py` ya existe en el repo — es tu endpoint que une las 3 bases.

Verifica que esté registrado en `app.py` corriendo esto (abre VS Code: `code .` y busca). Si no estuviera, abre `app.py` y agrega estas dos líneas:

```python
from recursos.estadisticas import estadisticas_bp   # (debajo de los otros imports)
app.register_blueprint(estadisticas_bp)              # (debajo de los otros register_blueprint)
```

Luego, en el navegador: `http://localhost:5000/api/estadisticas/1` → debe responder un JSON con sitio_nombre, total_eventos y sesiones_activas.

En la terminal:

```powershell
git add app.py recursos/estadisticas.py
git commit -m "feat: endpoint /api/estadisticas que une MySQL + MongoDB + Redis"
git push
```

## COMMIT 2 — Mis casos de prueba

Verifica que existe `tests/pruebas_elias.py`. Córrelo en la terminal:

```powershell
python tests/pruebas_elias.py
```

Debe imprimir varios 201/200 con los recursos tuyos. Luego:

```powershell
git add tests/pruebas_elias.py
git commit -m "test: casos de prueba para paginas, objetivos y eventos"
git push
```

## COMMIT 3 — Mis notas en el README

Abre `README.md` con VS Code y agrega al final una sección con tu nombre:

```markdown
## Integrantes

- Ángel Salvador Álvarez Fernández — esqueleto del proyecto, recursos `usuarios`, `sitios`, `sesiones` (Redis), sitio de prueba y documentación.
- Elías Meléndez Guzmán — recursos `paginas`, `objetivos`, `eventos` (MongoDB), endpoint de estadísticas y archivo de pruebas.
```

Y guarda. Luego:

```powershell
git add README.md
git commit -m "docs: agrego seccion de integrantes al README"
git push
```

---

## LISTO. Verifica

Abre `https://github.com/eliasMG2/T3-01-Proyecto-Multibase-de-datos/graphs/contributors` y debe aparecer **tu nombre con 3 commits**.

Avísale a Ángel por WhatsApp cuando hayas hecho los 3 pushes. Él hace la entrega final en Classroom. **Antes de 9:30 a.m.** si puedes.
