# TITAN Racha — clon funcional inspirado en Racha Sports

Esta versión reproduce el patrón funcional de la aplicación de referencia: navegación por Fútbol / Tendencias / Ligas / Props, calendario de partidos, ficha del encuentro, probabilidades, matriz de marcadores, estadísticas y módulos para jugadores.

## Seguridad de la API key

La clave **no se escribe en el código**. Copia `.env.example` como `.env` y coloca ahí tu `API_FOOTBALL_KEY`.

## Instalación

```powershell
cd C:\ruta\racha_clone_titan
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
python -m streamlit run app.py
```

En Linux/macOS:

```bash
cp .env.example .env
python -m streamlit run app.py
```

## Endpoints usados

- `/fixtures`
- `/fixtures/statistics`
- `/predictions`
- `/leagues`
- `/players`

Para versiones siguientes podemos añadir standings, H2H, injuries, lineups, odds, eventos en vivo, caché avanzada y el motor TITAN.
