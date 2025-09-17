"""Inventory management logic."""

from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models
from ..repositories import InventoryRepository, ProductRepository
from ..schemas import InventoryAdjustment, ProductCreate, ProductUpdate


class InventoryService:
    def __init__(self, session: Session):
        self.session = session
        self.products = ProductRepository(session)
        self.inventory = InventoryRepository(session)

    def list_products(self, active_only: bool = False) -> list[models.Product]:
        return list(self.products.list_products(active_only=active_only))

    def create_product(self, payload: ProductCreate) -> models.Product:
        product = models.Product(
            name=payload.name,
            slot_code=payload.slot_code.upper(),
            price=float(payload.price),
            quantity=payload.quantity,
            is_active=payload.is_active,
        )
        self.products.create(product)
        if payload.quantity:
            self.inventory.log_event(
                models.InventoryEvent(product_id=product.id, change=payload.quantity, reason="initial_stock")
            )
        return product

    def update_product(self, product_id: int, payload: ProductUpdate) -> models.Product:
        product = self._get_product_or_error(product_id)
        if payload.name is not None:
            product.name = payload.name
        if payload.price is not None:
            product.price = float(payload.price)
        if payload.is_active is not None:
            product.is_active = payload.is_active
        if payload.quantity is not None:
            difference = payload.quantity - product.quantity
            product.quantity = payload.quantity
            if difference:
                self.inventory.log_event(
                    models.InventoryEvent(product_id=product.id, change=difference, reason="manual_adjustment")
                )
        self.session.flush()
        self.session.refresh(product)
        return product

    def adjust_inventory(self, adjustment: InventoryAdjustment) -> models.Product:
        product = self._get_product_or_error(adjustment.product_id)
        product.quantity += adjustment.change
        self.inventory.log_event(
            models.InventoryEvent(product_id=product.id, change=adjustment.change, reason=adjustment.reason)
        )
        self.session.flush()
        self.session.refresh(product)
        return product

    def _get_product_or_error(self, product_id: int) -> models.Product:
        product = self.products.get(product_id)
        if product is None:
            raise ValueError(f"Product {product_id} not found")
        return product
