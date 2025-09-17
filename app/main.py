"""Application entry point exposing the vending machine API."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, status

from .store import VendingMachine, ensure_decimal

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    """Create the application instance with routes bound to a store."""
    app = FastAPI(title="Brabus Right Vending")
    store = VendingMachine()

    @app.get("/")
    def root() -> dict[str, str]:  # pragma: no cover - trivial
        return {"message": "Brabus Right Vending online"}

    @app.post(f"{API_PREFIX}/admin/products", status_code=status.HTTP_201_CREATED)
    def create_product(payload: dict) -> dict:
        try:
            product = store.create_product(payload)
        except ValueError as exc:  # invalid payload
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return product

    @app.get(f"{API_PREFIX}/admin/products")
    def list_products() -> list[dict]:
        return store.list_products()

    @app.post(f"{API_PREFIX}/vending/purchase", status_code=status.HTTP_201_CREATED)
    def purchase(payload: dict) -> dict:
        try:
            sale = store.vend(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return sale

    @app.post(f"{API_PREFIX}/vending/telemetry/capture")
    def capture_telemetry() -> dict:
        return store.capture_telemetry()

    @app.get(f"{API_PREFIX}/vending/products")
    def vending_products() -> list[dict]:
        return store.list_products(active_only=True)

    @app.get(f"{API_PREFIX}/analytics/sales/summary")
    def sales_summary(days: int = 30) -> dict:
        # "days" is accepted for compatibility even though the mock store keeps
        # the data in-memory for the lifetime of the app instance.
        return store.sales_summary(days=days)

    @app.get(f"{API_PREFIX}/analytics/inventory/turnover")
    def inventory_turnover(days: int = 30) -> dict:
        return store.inventory_turnover(days=days)

    @app.get(f"{API_PREFIX}/analytics/telemetry/trend")
    def telemetry_trend(hours: int = 24) -> list[dict]:
        return store.telemetry_trend(hours=hours)

    return app


app = create_app()

__all__ = ["app", "create_app", "ensure_decimal"]
