"""Analytics helpers for dashboards and remote monitoring."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models
from ..repositories import SaleRepository, TelemetryRepository


class AnalyticsService:
    def __init__(self, session: Session):
        self.session = session
        self.sales_repo = SaleRepository(session)
        self.telemetry_repo = TelemetryRepository(session)

    def sales_summary(self, days: int = 30) -> dict:
        return self.sales_repo.aggregate_sales(days=days)

    def telemetry_trend(self, hours: int = 24) -> list[models.Telemetry]:
        limit = max(1, hours * 2)
        return list(self.telemetry_repo.latest(limit=limit))

    def inventory_turnover(self, days: int = 30) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=days)
        sales_stmt = (
            select(models.Product.slot_code, func.coalesce(func.sum(models.Sale.quantity), 0))
            .join(models.Sale.product)
            .where(
                models.Sale.created_at >= cutoff,
                models.Sale.status == models.SaleStatusEnum.SUCCESS,
            )
            .group_by(models.Product.id)
        )
        sold_map = {slot: int(quantity) for slot, quantity in self.session.execute(sales_stmt).all()}

        product_stmt = (
            select(models.Product)
            .where(models.Product.is_active.is_(True))
            .order_by(models.Product.slot_code)
        )
        products = self.session.scalars(product_stmt).all()

        return {
            "as_of": datetime.utcnow(),
            "products": [
                {
                    "name": product.name,
                    "slot_code": product.slot_code,
                    "quantity_on_hand": product.quantity,
                    "sold_last_period": sold_map.get(product.slot_code, 0),
                    "last_updated": product.updated_at,
                }
                for product in products
            ],
        }
