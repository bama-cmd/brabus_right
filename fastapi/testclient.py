"""Very small HTTP client used for unit testing the FastAPI shim."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from . import HTTPException


def _split_url(url: str) -> tuple[str, Dict[str, str]]:
    if "?" not in url:
        return url, {}
    path, query = url.split("?", 1)
    params: Dict[str, str] = {}
    for pair in query.split("&"):
        if not pair:
            continue
        if "=" in pair:
            key, value = pair.split("=", 1)
        else:
            key, value = pair, ""
        params[key] = value
    return path, params


@dataclass
class Response:
    status_code: int
    _json: Any

    def json(self) -> Any:
        return self._json


class TestClient:
    def __init__(self, app: Any) -> None:
        self._app = app

    # HTTP verb helpers --------------------------------------------------------
    def get(self, url: str, params: Optional[dict[str, Any]] = None) -> Response:
        return self.request("GET", url, params=params)

    def post(self, url: str, json: Optional[dict[str, Any]] = None) -> Response:
        return self.request("POST", url, json=json)

    def patch(self, url: str, json: Optional[dict[str, Any]] = None) -> Response:
        return self.request("PATCH", url, json=json)

    def request(self, method: str, url: str, *, params: Optional[dict[str, Any]] = None, json: Optional[dict[str, Any]] = None) -> Response:
        path, inline_params = _split_url(url)
        merged_params = {**inline_params, **(params or {})}
        try:
            status_code, data = self._app.handle_request(method, path, json=json, params=merged_params)
        except HTTPException as exc:  # pragma: no cover - should not be triggered directly in tests
            status_code = exc.status_code
            data = {"detail": exc.detail}
        return Response(status_code=status_code, _json=data)

    # Context manager interface -------------------------------------------------
    def __enter__(self) -> "TestClient":  # pragma: no cover - used by pytest fixture
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - no cleanup required
        return None
