import threading
import time

import requests

BASE_URL = "https://api.scryfall.com"
HEADERS = {
    "User-Agent": "scry-cli/0.1.0",
    "Accept": "application/json;q=0.9,*/*;q=0.8",
}

MIN_INTERVAL = 0.200  # 200ms between requests = max 5 req/s

_last_request_time: float = 0.0
_lock = threading.Lock()


def _rate_limit() -> None:
    global _last_request_time
    with _lock:
        now = time.monotonic()
        elapsed = now - _last_request_time
        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)
        _last_request_time = time.monotonic()


class ScryfallClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _get(self, path: str, params: dict | None = None) -> dict:
        _rate_limit()
        resp = self.session.get(f"{BASE_URL}{path}", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def card_named(self, name: str, exact: bool = False) -> dict:
        param_key = "exact" if exact else "fuzzy"
        return self._get("/cards/named", params={param_key: name})

    def card_search(self, query: str, page: int = 1) -> dict:
        return self._get("/cards/search", params={"q": query, "page": page})

    def card_random(self, query: str | None = None) -> dict:
        params = {"q": query} if query else None
        return self._get("/cards/random", params=params)
