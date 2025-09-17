"""Data access helpers for domain models."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from . import models


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_products(self, active_only: bool = False) -> Sequence[models.Product]:
        stmt = select(models.Product)
        if active_only:
            stmt = stmt.where(models.Product.is_active.is_(True))
        stmt = stmt.order_by(models.Product.slot_code)
        return self.session.scalars(stmt).all()

    def get(self, product_id: int) -> models.Product | None:
        return self.session.get(models.Product, product_id)

    def get_by_slot(self, slot_code: str) -> models.Product | None:
        stmt = select(models.Product).where(models.Product.slot_code == slot_code)
        return self.session.scalars(stmt).first()

    def create(self, product: models.Product) -> models.Product:
        self.session.add(product)
        self.session.flush()
        return product

    def delete(self, product: models.Product) -> None:
        self.session.delete(product)


class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def log_event(self, event: models.InventoryEvent) -> models.InventoryEvent:
        self.session.add(event)
        self.session.flush()
        return event


class SaleRepository:
    def __init__(self, session: Session):
        self.session = session

    def record(self, sale: models.Sale) -> models.Sale:
        self.session.add(sale)
        self.session.flush()
        self.session.refresh(sale)
        return sale

    def aggregate_sales(self, days: int = 30) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=days)
        stmt = select(
            func.count(models.Sale.id),
            func.coalesce(func.sum(models.Sale.total_price), 0),
        ).where(models.Sale.created_at >= cutoff, models.Sale.status == models.SaleStatusEnum.SUCCESS)
        count, revenue = self.session.execute(stmt).one()

        top_stmt = (
            select(models.Product.name, func.count(models.Sale.id).label("count"))
            .join(models.Sale.product)
            .where(models.Sale.created_at >= cutoff, models.Sale.status == models.SaleStatusEnum.SUCCESS)
            .group_by(models.Product.id)
            .order_by(desc("count"))
            .limit(5)
        )
        top_products = [
            {"name": name, "sales": int(sales)}
            for name, sales in self.session.execute(top_stmt).all()
        ]

        average_ticket = Decimal(revenue) / count if count else Decimal("0")

        return {
            "total_sales": int(count),
            "total_revenue": Decimal(revenue),
            "average_ticket": average_ticket.quantize(Decimal("0.01")) if count else Decimal("0"),
            "top_products": top_products,
        }


class TelemetryRepository:
    def __init__(self, session: Session):
        self.session = session

    def log(self, telemetry: models.Telemetry) -> models.Telemetry:
        self.session.add(telemetry)
        self.session.flush()
        self.session.refresh(telemetry)
        return telemetry

    def latest(self, limit: int = 50) -> Sequence[models.Telemetry]:
        stmt = select(models.Telemetry).order_by(models.Telemetry.created_at.desc()).limit(limit)
        return list(reversed(self.session.scalars(stmt).all()))


class DeviceStateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create(self) -> models.DeviceState:
        state = self.session.scalar(select(models.DeviceState))
        if state is None:
            state = models.DeviceState(door_locked=True)
            self.session.add(state)
            self.session.flush()
        return state

    def update(self, door_locked: bool) -> models.DeviceState:
        state = self.get_or_create()
        state.door_locked = door_locked
        self.session.flush()
        self.session.refresh(state)
        return state
