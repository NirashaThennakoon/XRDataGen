from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any
import requests
from requests.adapters import HTTPAdapter, Retry

class SCDMClient:
    def __init__(self, api_base: str, email: str|None, password: str|None):
        self.api_base = api_base.rstrip("/")
        self.email = email
        self.password = password
        self._token: str|None = None
        self._expires_at = datetime.now(timezone.utc)

        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3,
                        status_forcelist=(429, 500, 502, 503, 504),
                        allowed_methods=frozenset(['GET','POST']))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def _login(self) -> str:
        url = f"{self.api_base}/api/auth/login"
        payload = {
            "email": self.email,
            "password": self.password,
            "firstName": "Nirasha",
            "lastName": "Thennakoon",
            "intent": "Student",
            "organization": "University of Oulu",
        }
        r = self.session.post(url, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        token = data.get("token") or data.get("access_token")
        if not token:
            raise RuntimeError("Login response missing token")
        self._token = f"Bearer {token}"
        self._expires_at = datetime.now(timezone.utc) + timedelta(minutes=50)
        return self._token

    def _auth_header(self) -> dict[str,str]:
        now = datetime.now(timezone.utc)
        if not self._token or self._expires_at <= now:
            self._login()
        return {"Authorization": self._token, "Accept": "application/json"}

    def events(self, from_iso: str, to_iso: str, metrics: str = "co2") -> list[dict[str, Any]]:
        url = f"{self.api_base}/api/events.json"
        params = {"from": from_iso, "to": to_iso, "metrics": metrics}
        r = self.session.get(url, headers=self._auth_header(), params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            raise ValueError("Unexpected events response")
        return data
