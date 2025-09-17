"""In-memory data store and operations for the vending machine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from itertools import count
from typing import Dict, List


MONEY_QUANTIZE = Decimal("0.01")


def ensure_decimal(value: object) -> Decimal:
    """Convert supported inputs into a quantised Decimal."""
    if isinstance(value, Decimal):
        result = value
    else:
        try:
            result = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:  # pragma: no cover - defensive
            raise ValueError("Invalid monetary value") from exc
    return result.quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)


@dataclass
class Product:
    id: int
    name: str
    slot_code: str
    price: Decimal
    quantity: int
    is_active: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Sale:
    id: int
    product_id: int
    quantity: int
    total_price: Decimal
    payment_method: str
    amount_paid: Decimal
    status: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Telemetry:
    id: int
    temperature_c: float
    humidity: float
    door_open: bool
    created_at: datetime = field(default_factory=datetime.utcnow)


class VendingMachine:
    """Minimal, deterministic store suitable for unit testing."""

    def __init__(self) -> None:
        self._products: Dict[int, Product] = {}
        self._sales: List[Sale] = []
        self._telemetry: List[Telemetry] = []
        self._product_ids = count(1)
        self._sale_ids = count(1)
        self._telemetry_ids = count(1)

    # ------------------------------------------------------------------
    # Product management helpers
    # ------------------------------------------------------------------
    def create_product(self, payload: dict) -> dict:
        name = self._require_str(payload.get("name"), "name")
        slot_code = self._require_str(payload.get("slot_code"), "slot_code")
        price = ensure_decimal(payload.get("price"))
        quantity = self._require_int(payload.get("quantity", 0), "quantity", min_value=0)
        is_active = bool(payload.get("is_active", True))

        if any(p.slot_code.lower() == slot_code.lower() for p in self._products.values()):
            raise ValueError("Slot code already exists")

        product = Product(
            id=next(self._product_ids),
            name=name,
            slot_code=slot_code,
            price=price,
            quantity=quantity,
            is_active=is_active,
        )
        self._products[product.id] = product
        return self._serialise_product(product)

    def list_products(self, active_only: bool = False) -> List[dict]:
        products = self._products.values()
        if active_only:
            products = [p for p in products if p.is_active and p.quantity > 0]
        return [self._serialise_product(p) for p in products]

    # ------------------------------------------------------------------
    # Vending operations
    # ------------------------------------------------------------------
    def vend(self, payload: dict) -> dict:
        product_id = self._require_int(payload.get("product_id"), "product_id", min_value=1)
        quantity = self._require_int(payload.get("quantity"), "quantity", min_value=1)
        payment_method = self._require_str(payload.get("payment_method"), "payment_method")
        amount_paid = ensure_decimal(payload.get("amount_paid"))

        product = self._products.get(product_id)
        if product is None:
            raise ValueError("Product not found")
        if not product.is_active:
            raise ValueError("Product is inactive")
        if product.quantity < quantity:
            raise ValueError("Insufficient inventory")

        total_price = ensure_decimal(product.price * quantity)
        if amount_paid < total_price:
            raise ValueError("Insufficient payment")

        product.quantity -= quantity
        product.updated_at = datetime.utcnow()

        sale = Sale(
            id=next(self._sale_ids),
            product_id=product.id,
            quantity=quantity,
            total_price=total_price,
            payment_method=payment_method,
            amount_paid=amount_paid,
            status="success",
        )
        self._sales.append(sale)
        return self._serialise_sale(sale)

    # ------------------------------------------------------------------
    # Telemetry
    # ------------------------------------------------------------------
    def capture_telemetry(self) -> dict:
        # For testing we produce deterministic but varying readings.
        base_temp = 4.0
        base_humidity = 42.0
        sequence = len(self._telemetry)
        telemetry = Telemetry(
            id=next(self._telemetry_ids),
            temperature_c=base_temp + min(sequence, 5) * 0.1,
            humidity=base_humidity + (sequence % 3) * 0.5,
            door_open=False,
        )
        self._telemetry.append(telemetry)
        return self._serialise_telemetry(telemetry)

    def telemetry_trend(self, hours: int = 24) -> List[dict]:
        if hours <= 0:
            return []
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [self._serialise_telemetry(t) for t in self._telemetry if t.created_at >= cutoff]

    # ------------------------------------------------------------------
    # Analytics helpers
    # ------------------------------------------------------------------
    def sales_summary(self, days: int = 30) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=max(days, 0))
        sales = [sale for sale in self._sales if sale.created_at >= cutoff]
        total_sales = len(sales)
        total_revenue = sum((sale.total_price for sale in sales), Decimal("0"))
        average_ticket = total_revenue / total_sales if total_sales else Decimal("0")

        per_product: Dict[int, int] = {}
        for sale in sales:
            per_product[sale.product_id] = per_product.get(sale.product_id, 0) + sale.quantity

        top_products = [
            {
                "name": self._products[product_id].name,
                "sales": quantity,
            }
            for product_id, quantity in sorted(per_product.items(), key=lambda item: item[1], reverse=True)
        ]

        return {
            "total_sales": total_sales,
            "total_revenue": str(ensure_decimal(total_revenue)),
            "average_ticket": str(ensure_decimal(average_ticket)),
            "top_products": top_products,
        }

    def inventory_turnover(self, days: int = 30) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=max(days, 0))
        sold_map: Dict[int, int] = {pid: 0 for pid in self._products}
        for sale in self._sales:
            if sale.created_at >= cutoff:
                sold_map[sale.product_id] = sold_map.get(sale.product_id, 0) + sale.quantity

        products = [
            {
                "name": product.name,
                "slot_code": product.slot_code,
                "quantity_on_hand": product.quantity,
                "sold_last_period": sold_map.get(product.id, 0),
                "last_updated": product.updated_at.isoformat(),
            }
            for product in self._products.values()
        ]
        return {"as_of": datetime.utcnow().isoformat(), "products": products}

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------
    def _serialise_product(self, product: Product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "slot_code": product.slot_code,
            "price": str(ensure_decimal(product.price)),
            "quantity": product.quantity,
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat(),
        }

    def _serialise_sale(self, sale: Sale) -> dict:
        return {
            "id": sale.id,
            "product_id": sale.product_id,
            "quantity": sale.quantity,
            "total_price": str(ensure_decimal(sale.total_price)),
            "payment_method": sale.payment_method,
            "status": sale.status,
            "error_message": None,
            "created_at": sale.created_at.isoformat(),
        }

    def _serialise_telemetry(self, telemetry: Telemetry) -> dict:
        return {
            "id": telemetry.id,
            "temperature_c": telemetry.temperature_c,
            "humidity": telemetry.humidity,
            "door_open": telemetry.door_open,
            "created_at": telemetry.created_at.isoformat(),
        }

    # ------------------------------------------------------------------
    # Simple validators
    # ------------------------------------------------------------------
    @staticmethod
    def _require_str(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        return value.strip()

    @staticmethod
    def _require_int(value: object, field: str, *, min_value: int | None = None) -> int:
        if not isinstance(value, int):
            raise ValueError(f"{field} must be an integer")
        if min_value is not None and value < min_value:
            raise ValueError(f"{field} must be >= {min_value}")
        return value
