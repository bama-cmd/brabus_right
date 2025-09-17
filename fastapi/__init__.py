"""A minimal FastAPI-compatible shim used for the kata environment."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional


class HTTPException(Exception):
    """Simplified HTTP exception mirroring FastAPI's behaviour."""

    def __init__(self, status_code: int, detail: Any = None) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class Depends:  # pragma: no cover - present for API compatibility only
    def __init__(self, dependency: Callable[..., Any]):
        self.dependency = dependency


@dataclass
class Route:
    path: str
    methods: List[str]
    endpoint: Callable[..., Any]
    status_code: Optional[int] = None


class APIRouter:
    """Collects routes to be attached to an application."""

    def __init__(self) -> None:
        self.routes: list[Route] = []

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: Iterable[str],
        *,
        status_code: Optional[int] = None,
    ) -> None:
        self.routes.append(Route(path=path, methods=[m.upper() for m in methods], endpoint=endpoint, status_code=status_code))

    def route(self, path: str, *, methods: Iterable[str], status_code: Optional[int] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, methods, status_code=status_code)
            return func

        return decorator

    def get(self, path: str, *, status_code: Optional[int] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=["GET"], status_code=status_code)

    def post(self, path: str, *, status_code: Optional[int] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=["POST"], status_code=status_code)

    def patch(self, path: str, *, status_code: Optional[int] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, methods=["PATCH"], status_code=status_code)


class FastAPI(APIRouter):
    """Very small subset of FastAPI adequate for the unit tests."""

    def __init__(self, *, title: str | None = None) -> None:
        super().__init__()
        self.title = title or "FastAPI"
        self._middleware: list[tuple[Any, dict[str, Any]]] = []

    # Application-level helpers -------------------------------------------------
    def include_router(self, router: APIRouter, *, prefix: str = "") -> None:
        for route in router.routes:
            self.add_api_route(prefix + route.path, route.endpoint, route.methods, status_code=route.status_code)

    def add_middleware(self, middleware_class: Any, **options: Any) -> None:  # pragma: no cover - provided for completeness
        self._middleware.append((middleware_class, options))

    # HTTP handling -------------------------------------------------------------
    def handle_request(self, method: str, path: str, *, json: Any = None, params: Optional[dict[str, Any]] = None) -> tuple[int, Any]:
        method = method.upper()
        params = params or {}
        for route in self.routes:
            if method in route.methods and route.path == path:
                try:
                    result = _call_endpoint(route.endpoint, json, params)
                except HTTPException as exc:
                    return exc.status_code, {"detail": exc.detail}
                status_code = route.status_code or 200
                if isinstance(result, tuple) and len(result) == 2:
                    body, route_status = result
                    if route_status is not None:
                        status_code = route_status
                else:
                    body = result
                return status_code, body
        raise HTTPException(status_code=404, detail="Not Found")


def _call_endpoint(endpoint: Callable[..., Any], json_payload: Any, params: dict[str, Any]) -> Any:
    import inspect

    signature = inspect.signature(endpoint)
    kwargs: dict[str, Any] = {}
    for name, parameter in signature.parameters.items():
        if name == "payload":
            kwargs[name] = json_payload
        elif name in params:
            kwargs[name] = params[name]
        elif parameter.default is not inspect._empty:
            kwargs[name] = parameter.default
        else:
            # Endpoint expects a body but the caller did not provide one.
            raise HTTPException(status_code=400, detail=f"Missing parameter: {name}")
    return endpoint(**kwargs)


class status:
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_404_NOT_FOUND = 404


__all__ = [
    "APIRouter",
    "Depends",
    "FastAPI",
    "HTTPException",
    "status",
]
