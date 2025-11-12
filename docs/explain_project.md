# 🧩 Explicación Integral del Proyecto AgroSense Tech

Bienvenido: aquí entenderás, paso a paso y desde cero, qué es AgroSense Tech, cómo está organizado el código, cómo fluyen los datos desde los sensores hasta el dashboard, cómo se prueba su calidad y qué estándares seguimos (ISO/IEC 25010, ISO/IEC 29119, ISTQB).

---

## 🎯 Qué es AgroSense Tech y por qué existe

- AgroSense Tech es una plataforma IoT de monitoreo agrícola. Recibe lecturas de sensores (temperatura, humedad, pH, luz), las almacena, calcula métricas agregadas y las muestra en un dashboard web.
- Problema que resuelve: dar visibilidad rápida y fiable del estado del cultivo para tomar decisiones (riego, luz, correcciones de pH). Conecta IoT (captura) + análisis de datos (métricas) + automatización (visualización, CI/CD, pruebas).
- Estándares de calidad:
  - ISO/IEC 25010: guía de atributos de calidad (fiabilidad, mantenibilidad, usabilidad…).
  - ISO/IEC 29119: proceso de pruebas (planificación → ejecución → reporte).
  - ISTQB: técnicas y niveles de prueba (caja negra, caja blanca; unitarias, integración, sistema, aceptación).

---

## 🧱 Visión general de la estructura

Carpetas y archivos clave en la raíz del repositorio:

- `main.py`: crea la app FastAPI, registra routers, inicializa la BD y redirige `/` → `/dashboard/view`.
- `database.py`: motor SQLAlchemy, `SessionLocal`, `Base`, `init_db()`, `get_db()`, y `get_connection()` (psycopg2). Admite `PostgreSQL` o `SQLite` (fallback).
- `models.py`: modelo ORM `Sensor` y esquemas Pydantic para validar/serializar datos.
- `routers/`:
  - `sensors.py`: POST `/sensor-data` (ingesta de lecturas).
  - `analytics.py`: GET `/analytics` (métricas avg/max/min) y función `process_data()`.
  - `dashboard.py`: GET `/dashboard` (resumen JSON para frontends o integraciones).
  - `dashboard_html.py`: GET `/dashboard/view` (render HTML con Jinja2).
- `templates/dashboard.html`: plantilla del dashboard (Jinja2 + Plotly.js).
- `scripts/`: herramientas para sembrar/verificar la base de datos (`seed_from_sql.py`, `seed_db.py`, `verify_connection.py`).
- `tests/`: suite de pruebas (unitarias, integración, sistema) con pytest.
- `.github/workflows/ci.yml`: pipeline de CI (instalación, pruebas, cobertura, artefactos).
- `docs/`: documentación LaTeX/IEEE y diagramas Mermaid.
- `docker-compose.yml`: stack listo (Postgres + app) para un entorno reproducible.

Cómo se conectan las piezas (flujo de trabajo de alto nivel):
1) Cliente (sensor o script) envía una lectura a POST `/sensor-data`.
2) La API valida y guarda en la base (SQLAlchemy ORM).
3) El dashboard y los endpoints de analítica leen las lecturas, calculan métricas y devuelven JSON o HTML.
4) La suite de pruebas verifica estos flujos y el pipeline CI las ejecuta automáticamente.

---

## ⚙️ Backend y API (FastAPI)

FastAPI es el framework que expone los endpoints REST.

- App principal: `main.py`
  - Llama a `init_db()` al arrancar para crear tablas.
  - Registra routers: `sensors`, `analytics`, `dashboard`, `dashboard_html`.
  - Redirección útil: `/` → `/dashboard/view`.

Routers principales:
- `routers/sensors.py` (ingesta)
  - Endpoint: `POST /sensor-data`.
  - Entrada validada con Pydantic (`SensorCreate`): `sensor_id`, `temperature`, `humidity`, `ph`, `light`, `timestamp` (opcional).
  - Persiste una instancia `Sensor` (ORM) y confirma con `commit()`.
- `routers/analytics.py` (analítica)
  - Endpoint: `GET /analytics`.
  - Consulta todas las lecturas, arma una lista de dicts y llama a `process_data()`.
  - Devuelve un JSON con sub-objetos por variable: `temperature`, `humidity`, `ph`, `light`; cada uno con `avg`, `max`, `min`.
- `routers/dashboard.py` (resumen JSON)
  - Endpoint: `GET /dashboard`.
  - Similar a analytics, pero además incluye `count` de lecturas y algunas métricas de conveniencia.
- `routers/dashboard_html.py` (vista HTML)
  - Endpoint: `GET /dashboard/view`.
  - Renderiza `templates/dashboard.html` con `Jinja2Templates`.

Swagger y documentación interactiva:
- FastAPI expone automáticamente la documentación en:
  - Swagger UI: `http://127.0.0.1:8000/docs`
  - Redoc: `http://127.0.0.1:8000/redoc`
- Para “buscar el Swagger en Google”: basta con abrir el navegador y escribir `localhost:8000/docs` o, si está desplegado con un dominio, `https://tu-dominio/docs`.

Validación con Pydantic (v2):
- `models.py` define `SensorCreate` (entrada) y `SensorOut` (salida). Con `ConfigDict(from_attributes=True)` podemos serializar desde objetos ORM sin esfuerzo.

---

## 🗄️ Persistencia y Base de Datos (SQLAlchemy + PostgreSQL/SQLite)

Modelos ORM:
- `models.Sensor` mapea la tabla `sensor_data` con columnas: `id`, `sensor_id`, `temperature`, `humidity`, `ph`, `light`, `timestamp` (con `server_default=func.now()`).

Sesión y motor:
- `database.SessionLocal`: factoría de sesiones.
- `database.get_db()`: dependencia FastAPI que abre una sesión por request y la cierra al final (patrón recomendado).
- `database.init_db()`: importa modelos y crea tablas (`Base.metadata.create_all`).

Conexión y configuración:
- Prioridad para elegir motor (`database.DATABASE_URL`):
  1) `POSTGRES_DSN` (si se define explícitamente),
  2) `DATABASE_URL`,
  3) fallback `sqlite:///agrosense.db`.
- Para diagnósticos directos con psycopg2: `database.get_connection()` resuelve DSN (Postgres) y devuelve una conexión con `RealDictCursor`.

Scripts de apoyo (carpeta `scripts/`):
- `verify_connection.py`: imprime variables relevantes y verifica conexión a Postgres.
- `seed_from_sql.py`: ejecuta `scripts/seed_data.sql` (crea/llena la tabla y una vista ejemplo).
- `seed_db.py`: siembra lecturas de ejemplo usando el ORM.

Notas prácticas:
- Para desarrollo local con rapidez, puedes usar SQLite (sin levantar Postgres). Para demos y producción, usa PostgreSQL.
- Se soporta `.env` (si `python-dotenv` está instalado) para cargar `DATABASE_URL` y `POSTGRES_*` sin exponer credenciales en el repo.

---

## 📊 Dashboard y visualización (Jinja2 + Plotly.js)

Plantilla: `templates/dashboard.html`
- Estructura visual con CSS + KPIs + 4 gráficos de barras (Plotly.js) para temperatura, humedad, pH y luz.
- Carga datos de `/analytics` vía `fetch` y actualiza KPIs y gráficas.
- Botón “Actualizar” y marca de tiempo de la última actualización.

Relación con el backend:
- La vista HTML puede renderizarse servidor-side (`/dashboard/view`) o consumirse via JSON (`/analytics`).
- El cálculo de métricas lo centraliza `process_data()` para evitar duplicidad de lógica.

Tip útil:
- Puedes “guardar” la página ya renderizada sin servidor usando un cliente de prueba (se dejó un ejemplo en el README para generar `dashboard_view.html`).

---

## 🧪 Pruebas y Calidad (pytest + cobertura)

Estructura de `tests/`:
- `test_unit/`: pruebas unitarias (p. ej., `test_process_data.py`, `test_database_helpers.py`, `test_sensors_unit.py`).
- `test_integration/`: integración de endpoints y DB (`test_analytics_integration.py`, `test_dashboard_integration.py`, `test_dashboard_json_integration.py`).
- `test_system/`: end-to-end (`test_end_to_end.py`).
- `conftest.py`: fixtures compartidas (`client` y `db_session`).
- Algunos archivos “placeholder” documentan consolidaciones de tests legados.

Tipos de pruebas:
- Unitarias: funciones puras (como `process_data`) y helpers de DB.
- Integración: routers + persistencia (verifican JSON, estados vacíos y consistencia).
- Sistema (E2E): ingesta → analítica; confirma que min/max/avg cubren los valores enviados.

Fixtures:
- `client`: instancia `TestClient(app)` para llamadas HTTP internas.
- `db_session`: crea y limpia la tabla de sensor antes de cada prueba (aislamiento y repetibilidad, alineado a ISO/IEC 29119).

Cobertura:
- La CI ejecuta `pytest --cov=.` y publica reportes HTML/XML como artefactos.
- Cobertura global actual: ~91% (según los reportes LaTeX y CI). Esto refleja buena mantenibilidad y testabilidad (ISO/IEC 25010).

Pruebas críticas (qué validan):
- `/sensor-data` acepta payload válido y rechaza entradas inválidas (tipos y campos faltantes).
- `/analytics` devuelve estructura anidada con `avg`, `max`, `min` y se comporta bien si no hay datos.
- `/dashboard/view` carga el HTML y muestra el branding; `/dashboard` (JSON) reporta `count` y métricas.
- Helpers de `database.py` manejan la selección de DSN, la creación de tablas y errores de conexión coherentemente.

---

## 🤖 Automatización y CI/CD (GitHub Actions)

Archivo: `.github/workflows/ci.yml`
- Se ejecuta en `push` y `pull_request` contra `main`.
- Estrategia de matrices Python 3.11 y 3.12.
- Pasos principales:
  1) Instala dependencias (incluye `psycopg2-binary` y librerías del sistema para compilar si hiciera falta).
  2) Ejecuta `pytest` con cobertura (term, XML y HTML) y sube artefactos de cobertura (`htmlcov/`, `coverage.xml`, `.coverage.*`).
  3) Job adicional que combina cobertura “raw” entre versiones y publica un HTML/XML combinado (cuando corresponde).

¿Por qué es importante?
- Ejecuta pruebas en entornos limpios (reproducibles).
- Detecta regresiones temprano.
- Sirve de evidencia objetiva de proceso (ISO/IEC 29119) y respalda atributos de calidad (ISO/IEC 25010: fiabilidad, mantenibilidad, portabilidad).

---

## 🧭 Arquitectura y diagramas (Mermaid)

Archivos en `docs/`:
- `diagrama_arquitectura.mmd`: visión “ampliada” orientada a nube (AWS IoT Core, Kinesis, Lambda, Timestream, DynamoDB, S3, SageMaker, API Gateway, Cognito, CloudFront, ECS). Muestra un pipeline típico: sensores → ingesta → procesamiento → almacenamiento → analítica/ML → API → frontend/CDN → navegador.
- `web_application_architecture.mmd`: maqueta de aplicación web que ilustra roles de “servidor de aplicación”, “base de datos” y “frontend”. Aunque menciona “Flask” y “Chart.js” (genérico), en este proyecto los equivalentes reales son FastAPI y Plotly.js.

Flujo de datos explicado (de extremo a extremo):
1) Sensores envían lecturas (IoT). En la demo, lo simulas con requests al endpoint de ingesta.
2) Backend recibe, valida y almacena (FastAPI + SQLAlchemy + Postgres/SQLite).
3) El servicio de analítica agrega y expone métricas (GET `/analytics`).
4) El dashboard (Jinja2 + Plotly.js) consulta esas métricas y las visualiza.
5) CI/CD valida continuamente que estos flujos sigan funcionando.

---

## 🧠 Estándares aplicados (ISO/IEC 25010, ISO/IEC 29119, ISTQB)

- ISO/IEC 25010 (calidad del producto):
  - Adecuación funcional: endpoints cumplen con su propósito (ingesta, analítica, visualización) y están cubiertos por pruebas.
  - Fiabilidad: suite multi-nivel sin fallos críticos; manejo de estados vacíos.
  - Mantenibilidad: arquitectura modular, alta cobertura, comentarios y separación de responsabilidades.
  - Usabilidad: dashboard claro con KPIs y gráficos.
  - Portabilidad/Compatibilidad: configuración por entorno; corre en Linux/Windows; fallback a SQLite.
- ISO/IEC 29119 (proceso de pruebas):
  - Evidencias: plan LaTeX (`plan_pruebas_agrosense.tex`), reporte (`reporte_pruebas.tex`), criterios de entrada/salida, trazabilidad.
  - Actividades: planificación → diseño → implementación → ejecución (CI) → evaluación/cierre.
- ISTQB (técnicas y niveles):
  - Caja negra: validación de endpoints y contratos de respuesta.
  - Caja blanca: paths internos (helpers, bordes de agregación). 
  - Niveles: unitarias, integración, sistema; aceptación planificada.

¿Dónde se evidencia en el repo?
- Código comentado (routers, `database.py`, `models.py`).
- Suite `tests/` organizada por niveles.
- CI que ejecuta y reporta cobertura.
- Documentos en `docs/` con plan, reporte y contexto.

---

## 📚 Documentación y evidencias (LaTeX, métricas)

En `docs/`:
- `plan_pruebas_agrosense.tex`: plan de pruebas (IEEEtran) — objetivos, alcance, estrategia, trazabilidad a ISO 25010 e ISO 29119, matriz de planificación.
- `reporte_pruebas.tex`: reporte de pruebas — resultados, cobertura (~91%), conclusiones y mejoras.
- `contexto_requerimientos_agrosense.tex`: contexto, buyer persona, requerimientos técnicos y estándares.
- Diagramas: `diagrama_arquitectura.mmd`, `web_application_architecture.mmd` (+ PNGs exportados).

Relaciones:
- Contexto → Plan → Ejecución en CI → Reporte (+ artefactos de cobertura). Las tablas y métricas dan evidencia objetiva para sustentar conclusiones.

---

## 🚀 Mejoras y extensiones sugeridas

Estado actual (completo):
- Ingesta, analítica y dashboard operativos.
- Persistencia con SQLAlchemy; Postgres preferido y SQLite de respaldo.
- Suite de pruebas multi-nivel y CI con cobertura.
- Documentación técnica y diagramas.

Pendiente / siguientes pasos de valor:
- Migraciones con Alembic (versionado del esquema en Postgres).
- Seguridad: autenticación/autorización (tokens), HTTPS y pruebas negativas 401/403.
- Rendimiento: simulador IoT para estrés/carga y umbrales en CI.
- Integración con Codecov para publicar tendencia de cobertura (objetivo ≥95%).
- Limpieza/curación de datos: reglas para filtrar lecturas inválidas (p. ej., valores cero por defecto de prueba) y endpoints de mantenimiento en dev.
- Despliegue: Docker Compose ya existe; extender a infraestructura cloud (por ejemplo, AWS ECS/Fargate + RDS + CloudFront) según el diagrama.

Cómo escalar a producción (ruta ejemplo):
1) Añadir Alembic y pipeline de migraciones.
2) Endpoints protegidos y secretos gestionados (AWS Secrets Manager/HashiCorp Vault).
3) Observabilidad: logs estructurados, métricas, trazas (OpenTelemetry).
4) CI/CD avanzado: Codecov + escaneo de seguridad + pruebas de carga en gates.
5) Infra: contenedores en ECS/Fargate o Kubernetes; RDS Postgres; CDN para estáticos.

---

## 📌 Referencias rápidas (uso)

- API Docs (Swagger): `http://127.0.0.1:8000/docs`
- Dashboard (HTML): `http://127.0.0.1:8000/dashboard/view`
- Métricas (JSON): `http://127.0.0.1:8000/analytics`
- Docker (rápido): `docker compose up -d --build`
- Tests locales: `python -m pytest -q`

---

Si necesitas una guía de presentación (paso a paso con comandos), ya está en `README.md` con flujo recomendado para mostrar al profesor.
