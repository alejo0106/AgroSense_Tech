# AgroSense Tech - Minimal FastAPI prototype

Project skeleton implementing two endpoints for sensor ingestion and a simple dashboard.

How to run

1. Create a virtual environment (optional) and install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run the app:

```powershell
python main.py
# or
uvicorn main:app --reload
```

3. Run tests:

```powershell
python -m pytest -q
```

## Diagrama del plan de pruebas

Pega el siguiente bloque en un visor que soporte Mermaid (por ejemplo GitHub README, VS Code con extensión Mermaid, o https://mermaid.live) para visualizar el flujo del plan de pruebas.

```mermaid
flowchart LR
	Start([Inicio del ciclo de pruebas])

	UT[Pruebas unitarias<br/>Herramienta: Pytest]
	IT[Pruebas de integración<br/>Herramientas: Pytest, Postman]
	ST[Pruebas de sistema<br/>Herramientas: Postman, Selenium / Playwright]
	AT[Pruebas de aceptación<br/>Herramientas: Postman, Pruebas manuales con stakeholders]
	Report([Entrega del informe técnico])

	Start --> UT --> IT --> ST --> AT --> Report

	classDef stage fill:#f8f9fa,stroke:#333,stroke-width:1px;
	class UT,IT,ST,AT stage;
```

Breve explicación: Unidad → Integración → Sistema → Aceptación, con herramientas sugeridas listadas en cada bloque.
