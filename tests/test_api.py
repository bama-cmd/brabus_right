from __future__ import annotations

import os
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

os.environ["PIVEND_DATABASE_URL"] = "sqlite:///./data/test_vending.db"

from pathlib import Path

DB_PATH = Path("data/test_vending.db")
if DB_PATH.exists():
    DB_PATH.unlink()

from app.main import create_app  # noqa: E402


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_full_vending_flow(client: TestClient) -> None:
    product_payload = {
        "name": "Soda",
        "slot_code": "A1",
        "price": "2.50",
        "quantity": 10,
        "is_active": True,
    }
    response = client.post("/api/v1/admin/products", json=product_payload)
    assert response.status_code == 201, response.json()
    product = response.json()
    product_id = product["id"]

    purchase_payload = {
        "product_id": product_id,
        "quantity": 2,
        "payment_method": "card",
        "amount_paid": "10.00",
    }
    purchase_response = client.post("/api/v1/vending/purchase", json=purchase_payload)
    assert purchase_response.status_code == 201, purchase_response.json()
    sale = purchase_response.json()
    assert sale["status"] == "success"
    assert sale["quantity"] == 2

    inventory_response = client.get("/api/v1/admin/products")
    assert inventory_response.status_code == 200
    inventory = inventory_response.json()
    remaining = next(item for item in inventory if item["id"] == product_id)
    assert remaining["quantity"] == 8

    telemetry_capture = client.post("/api/v1/vending/telemetry/capture")
    assert telemetry_capture.status_code == 200
    telemetry = telemetry_capture.json()
    assert "temperature_c" in telemetry

    summary_response = client.get("/api/v1/analytics/sales/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_sales"] >= 1
    assert Decimal(summary["total_revenue"]) >= Decimal("5.00")

    turnover_response = client.get("/api/v1/analytics/inventory/turnover")
    assert turnover_response.status_code == 200
    turnover = turnover_response.json()
    assert any(item["sold_last_period"] >= 2 for item in turnover["products"])
