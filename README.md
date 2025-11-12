# AgroSense_Tech — Proyecto FastAPI (Resumen y guía)

[![CI - pytest](https://github.com/alejo0106/AgroSense_Tech/actions/workflows/ci.yml/badge.svg)](https://github.com/alejo0106/AgroSense_Tech/actions/workflows/ci.yml)

Este repositorio es una pequeña aplicación demo que simula ingestión de datos de sensores IoT agrícolas y presenta un dashboard con métricas agregadas.

Este README está pensado para pegarse como contexto a otra instancia de ChatGPT o para compartir con un compañero; cubre TODO: estructura, endpoints, scripts, cómo ejecutar, qué cambié y notas de seguridad.

---

## Resumen rápido
- API en FastAPI con rutas para ingestión y métricas.
- Dashboard HTML (Jinja2 + Plotly) en `/dashboard/view`.
- Persistencia con SQLAlchemy: soporta SQLite (fallback) y PostgreSQL (vía `DATABASE_URL` o `POSTGRES_*`).
- Scripts para verificar conexión y para sembrar datos (SQL y ORM).
- Tests con `pytest` y CI con GitHub Actions.

Estado actual (local): conectada a Postgres en `localhost:5433` (usuario `postgres`, contraseña en `.env` local), seed ejecutado y métricas verificadas.

---

## Guía de presentación (orden recomendado)

El orden más rápido y claro para mostrar al profesor (elige A o B):

1) Base de datos y app
- Opción A (Docker, recomendado):
  ```powershell
  docker compose up -d --build
  ```
- Opción B (Local):
  ```powershell
  python -m venv .venv
  ./.venv/Scripts/Activate.ps1
  pip install -r requirements.txt
  # Crear .env a partir de .env.example o exportar variables POSTGRES_*
  python scripts\verify_connection.py
  python -m uvicorn main:app --reload
  ```

2) Sembrar datos (para que el dashboard muestre métricas)
- Docker:
  ```powershell
  docker compose exec app python scripts/seed_from_sql.py
  ```
- Local:
  ```powershell
  python scripts\seed_from_sql.py
  ```

3) Mostrar el dashboard y los endpoints
- Abrir Dashboard: http://127.0.0.1:8000/dashboard/view
- Ver JSON de métricas: http://127.0.0.1:8000/analytics
- (Opcional) Enviar una lectura de ejemplo:
  ```powershell
  $body = @{ sensor_id='demo-1'; temperature=24.5; humidity=68.2; ph=6.8; light=420 } | ConvertTo-Json
  Invoke-RestMethod -Uri http://127.0.0.1:8000/sensor-data -Method POST -Body $body -ContentType 'application/json'
  ```

4) Ejecutar los tests
- Docker:
  ```powershell
  docker compose exec app pytest -q
  ```
- Local:
  ```powershell
  python -m pytest -q
  ```

5) Evidencias (opcional)
- Ver logs de la app (Docker):
  ```powershell
  docker compose logs -f app
  ```
- Guardar dashboard como HTML estático:
  ```powershell
  python -c "import sys, os; sys.path.insert(0, r'.'); from fastapi.testclient import TestClient; from main import app; client = TestClient(app); open('dashboard_view.html','w',encoding='utf8').write(client.get('/dashboard/view').text)"
  ```

Problemas comunes (y solución rápida)
- “pytest no se reconoce”: usa `python -m pytest -q`.
- Error de conexión Postgres: ejecuta `python scripts\verify_connection.py` o usa Docker (`docker compose up -d`).
- Puerto ocupado (8000): cierra procesos anteriores o cambia a `--port 8001`.
- psycopg2 no instalado: `pip install -r requirements.txt`.

---

## Estructura del proyecto (archivos importantes)

- `main.py` — crea la app, inicializa la BD y registra routers. Redirige `/` → `/dashboard/view`.
- `database.py` — configuración de SQLAlchemy, `DATABASE_URL`, `engine`, `SessionLocal`, `init_db()`, `get_db()` y `get_connection()` (psycopg2 dinámico). Intenta cargar `.env` si `python-dotenv` está disponible.
- `models.py` — modelo ORM `Sensor` (tabla `sensor_data`) y schemas Pydantic.
- `routers/`
  - `sensors.py` — `POST /sensor-data` para ingestión.
  - `analytics.py` — `GET /analytics` y función `process_data()` que devuelve avg/max/min para temperatura, humedad, pH y luz.
  - `dashboard.py` — resumen JSON (si aplica).
  - `dashboard_html.py` — `GET /dashboard/view` que renderiza la plantilla con métricas.
- `templates/dashboard.html` — HTML + Plotly para visualización, consulta `/analytics` desde JS.
- `scripts/`
  - `verify_connection.py` — imprime env vars relevantes y prueba `get_connection()` (psycopg2) para Postgres.
  - `seed_db.py` — semilla de ejemplo (usa ORM y genera 5 lecturas aleatorias).
  - `seed_data.sql` — SQL DDL/DML (tabla, INSERTs y `sensor_metrics` view) con los datos que se proporcionaron.
  - `seed_from_sql.py` — ejecuta `seed_data.sql` contra la DB (usa `engine.exec_driver_sql`).
- `tests/` — tests unitarios e integración (suite previa en este workspace pasó verde).
- `requirements.txt` — dependencias (incluye `psycopg2-binary` y `python-dotenv`).
- `.env` — (local) creado durante la sesión con la `DATABASE_URL`; está en `.gitignore` y no debe subirse.
- `.gitignore` — excluye `.env`, `.venv`, `agrosense.db`, etc.
- `dashboard_view.html` — archivo HTML generado de la vista (guardado para abrir localmente).

---

## Endpoints principales

- POST `/sensor-data` — Ingesta de una lectura. Body pydantic con campos: `sensor_id`, `temperature`, `humidity`, `ph`, `light`, `timestamp`.
- GET `/analytics` — JSON con métricas agregadas (avg/max/min) para `temperature`, `humidity`, `ph` y `light`.
- GET `/dashboard/view` — HTML con Plotly que obtiene `/analytics` y muestra KPIs y gráficos.

Ejemplo de salida de `/analytics` (formato):

```json
{
  "temperature": { "avg": 24.3, "max": 29.1, "min": 20.4 },
  "humidity": { "avg": 68.9, "max": 74.0, "min": 61.0 },
  "ph": { "avg": 6.75, "max": 7.1, "min": 6.5 },
  "light": { "avg": 438.0, "max": 510.0, "min": 390.1 }
}
```

---

## Cómo configurar y ejecutar (PowerShell, Windows)

### Opción A: Entorno local

1) (Opcional) Crear y activar entorno virtual:

```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
```

2) Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3) Configurar la conexión a Postgres. Puedes crear un archivo `.env` en la raíz (NO lo subas al repo). Ejemplo (rellena con tus valores):

```
DATABASE_URL=postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>
```

Ejemplo (no subas este ejemplo con credenciales reales):

```
DATABASE_URL=postgresql://postgres:root@localhost:5433/AgroSense_Tech
```

Alternativa: exportar variables en la sesión PowerShell:

```powershell
$env:POSTGRES_USER='postgres'
$env:POSTGRES_PASSWORD='root'
$env:POSTGRES_HOST='localhost'
$env:POSTGRES_PORT='5433'
$env:POSTGRES_DB='AgroSense_Tech'
```

4) Verificar la conexión (recomendado):

```powershell
python scripts\verify_connection.py
```

Salida esperada: imprimirá `DATABASE_URL`, `engine.url`, `Inferred backend: postgresql` y `Connected to Postgres OK.` si la conexión es correcta.

5) Sembrar datos (si quieres usar los datos exactos suministrados):

```powershell
python scripts\seed_from_sql.py
```

Salida esperada: `Seed SQL executed successfully.`

6) Ejecutar la app:

```powershell
python -m uvicorn main:app --reload
```

Abrir:

- HTML: http://127.0.0.1:8000/dashboard/view
- JSON métricas: http://127.0.0.1:8000/analytics

7) Correr tests:

```powershell
pytest -q
```

---

### Opción B: Docker / docker-compose (recomendado para entorno consistente)

Requisitos: Docker Desktop instalado y en ejecución.

1) Copia `.env.example` a `.env` si quieres personalizar usuario/contraseña/DB.
2) Levanta los servicios (Postgres + app FastAPI):

```powershell
docker compose up -d --build
```

Esto inicia:
- Postgres en el puerto local `5433` mapeado al `5432` del contenedor.
- FastAPI en `http://localhost:8000` usando la variable `DATABASE_URL` apuntando al hostname `db`.

3) Ver logs de la aplicación:

```powershell
docker compose logs -f app
```

4) Ejecutar tests dentro del contenedor (rápido, sin instalar nada local):

```powershell
docker compose exec app pytest -q
```

5) Sembrar datos dentro del contenedor:

```powershell
docker compose exec app python scripts/seed_from_sql.py
```

6) Verificar conexión dentro del contenedor:

```powershell
docker compose exec app python scripts/verify_connection.py
```

Para apagar y eliminar contenedores:

```powershell
docker compose down
```

### Comandos rápidos (PowerShell) — qué ejecutan

Si prefieres copiar/pegar, aquí tienes los comandos más usados junto con una breve explicación de qué hace cada uno.

- Instalar dependencias:

```powershell
pip install -r requirements.txt
```
Qué hace: instala FastAPI, SQLAlchemy, psycopg2-binary, python-dotenv y otras dependencias necesarias.

- Verificar la conexión a la base de datos (usa `.env` o variables de entorno):

```powershell
python scripts\verify_connection.py
```
Qué hace: imprime `DATABASE_URL` y `POSTGRES_*`, muestra `engine.url` y prueba una conexión directa con psycopg2.

- Sembrar los datos proporcionados en `scripts/seed_data.sql` (crea tabla y vista):

```powershell
python scripts\seed_from_sql.py
```
Qué hace: ejecuta el SQL bruto (DDL + INSERTs + VIEW) en la base de datos configurada.

- Sembrar lecturas de ejemplo mediante ORM (script alternativo):

```powershell
python scripts\seed_db.py
```
Qué hace: usa SQLAlchemy ORM para crear 5 lecturas de ejemplo y guardarlas en la DB.

- Levantar la aplicación en modo desarrollo (uvicorn con recarga):

```powershell
python -m uvicorn main:app --reload
```
Qué hace: inicia el servidor web en http://127.0.0.1:8000 con recarga automática cuando detecta cambios de código.

- Guardar la vista HTML del dashboard en un archivo (se puede ejecutar en el repo):

```powershell
python -c "import sys, os; sys.path.insert(0, r'.'); from fastapi.testclient import TestClient; from main import app; client = TestClient(app); open('dashboard_view.html','w',encoding='utf8').write(client.get('/dashboard/view').text)"
```
Qué hace: renderiza la plantilla del dashboard en proceso y guarda el HTML en `dashboard_view.html` (útil para revisar sin abrir el navegador).

- Consultar el endpoint JSON de métricas (`/analytics`) desde PowerShell:

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/analytics -UseBasicParsing | Select-Object -ExpandProperty Content
```
Qué hace: obtiene el JSON de métricas y lo muestra en la consola.


## Notas técnicas y decisiones importantes

- El proyecto usa SQLAlchemy ORM para el modelo `Sensor` y Pydantic para validación de entrada.
- Se añadió soporte para leer `.env` con `python-dotenv` (opcional).
- `get_connection()` importa `psycopg2` dinámicamente para evitar warnings en linters/IDEs cuando el paquete no está instalado.
- El seed SQL original fallaba al `DROP TABLE` porque existía una `VIEW` dependiente; la SQL fue ajustada para `DROP VIEW IF EXISTS sensor_metrics` antes de dropear la tabla.
- `seed_from_sql.py` ejecuta el SQL en un bloque transaccional usando `engine.begin()` y `conn.exec_driver_sql(sql)`.
- Para renderizar el HTML del dashboard desde el entorno (sin uvicorn), se puede usar `fastapi.testclient.TestClient(app)` (esto es útil para generar y guardar `dashboard_view.html`).

---

## Seguridad y recomendaciones

- No subas `.env` ni credenciales al repositorio (está en `.gitignore`).
- No uses SQLite para producción — prefiera Postgres para concurrencia y migraciones reales.
- Agrega Alembic para manejar migraciones en Postgres.
- Protege endpoints sensibles si se exponen en entornos accesibles públicamente (auth, HTTPS, etc.).

---

## Qué cambié en esta sesión

- Añadí `python-dotenv` a `requirements.txt` y soporte de carga `.env` en `database.py`.
- Añadí `scripts/verify_connection.py` y `scripts/seed_from_sql.py`.
- Añadí `scripts/seed_data.sql` con los datos y la vista solicitados; ajusté para dropear la vista primero.
- Creé un `.env` local en el workspace con la `DATABASE_URL` que me diste (no se sube).
- Ejecuté `verify_connection.py` y `seed_from_sql.py` y confirmé la conexión y el seed.
- Guardé `dashboard_view.html` (render del dashboard) en la raíz.

---

## Siguientes pasos sugeridos (opcional)

- Añadir Alembic y migraciones.
- Añadir endpoint dev `/admin/db-info` (solo local) para diagnóstico.
- Añadir endpoint protegido para limpiar/sembrar datos en dev.
- Añadir README más corto en inglés si lo compartirás con externos.

---

Si quieres, genero ahora un `CHANGELOG.md` con los commits realizados durante esta sesión o agrego el endpoint admin. Dime qué prefieres.

---

Fecha del documento: 2025-11-12 (actualizado con Docker y mejoras de conexión Postgres)
# AgroSense_Tech