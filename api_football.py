import os
from typing import Any

import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
BASE = "https://v3.football.api-sports.io"

class APIError(RuntimeError):
    pass

class APIFootball:
    def __init__(self):
        self.key = os.getenv("API_FOOTBALL_KEY", "").strip()
        self.configured = bool(self.key)

    def _get(self, path: str, params: dict[str, Any] | None = None):
        if not self.configured:
            raise APIError("API_FOOTBALL_KEY no configurada.")
        try:
            r = requests.get(BASE + path, headers={"x-apisports-key": self.key, "Accept": "application/json"}, params=params or {}, timeout=25)
        except requests.RequestException as e:
            raise APIError(f"Error de conexión con API-Football: {e}") from e
        try:
            data = r.json()
        except ValueError as e:
            raise APIError(f"Respuesta no válida de API-Football ({r.status_code}).") from e
        if r.status_code >= 400:
            raise APIError(f"API-Football HTTP {r.status_code}: {data.get('message') or data}")
        errors = data.get("errors")
        if errors:
            raise APIError(f"API-Football: {errors}")
        return data.get("response", [])

    @st.cache_data(ttl=60, show_spinner=False)
    def fixtures_by_date(self, day: str): return self._get("/fixtures", {"date": day})
    @st.cache_data(ttl=30, show_spinner=False)
    def live_fixtures(self): return self._get("/fixtures", {"live": "all"})
    @st.cache_data(ttl=120, show_spinner=False)
    def fixture_detail(self, fixture_id: int): return self._get("/fixtures", {"id": fixture_id})
    @st.cache_data(ttl=3600, show_spinner=False)
    def predictions(self, fixture_id: int): return self._get("/predictions", {"fixture": fixture_id})
    @st.cache_data(ttl=60, show_spinner=False)
    def fixture_statistics(self, fixture_id: int): return self._get("/fixtures/statistics", {"fixture": fixture_id})
    @st.cache_data(ttl=30, show_spinner=False)
    def fixture_events(self, fixture_id: int): return self._get("/fixtures/events", {"fixture": fixture_id})
    @st.cache_data(ttl=300, show_spinner=False)
    def lineups(self, fixture_id: int): return self._get("/fixtures/lineups", {"fixture": fixture_id})
    @st.cache_data(ttl=3600, show_spinner=False)
    def h2h(self, home_id: int, away_id: int, last: int = 10): return self._get("/fixtures/headtohead", {"h2h": f"{home_id}-{away_id}", "last": last})
    @st.cache_data(ttl=3600, show_spinner=False)
    def standings(self, league_id: int, season: int): return self._get("/standings", {"league": league_id, "season": season})
    @st.cache_data(ttl=14400, show_spinner=False)
    def injuries(self, fixture_id: int): return self._get("/injuries", {"fixture": fixture_id})
    @st.cache_data(ttl=10800, show_spinner=False)
    def odds(self, fixture_id: int): return self._get("/odds", {"fixture": fixture_id})
    @st.cache_data(ttl=3600, show_spinner=False)
    def leagues(self, q: str | None = None): return self._get("/leagues", {"search": q} if q else {})
    @st.cache_data(ttl=3600, show_spinner=False)
    def players(self, search: str, league_id: int, season: int): return self._get("/players", {"search": search, "league": league_id, "season": season})
    @st.cache_data(ttl=21600, show_spinner=False)
    def team_statistics(self, team_id: int, league_id: int, season: int): return self._get("/teams/statistics", {"team": team_id, "league": league_id, "season": season})
