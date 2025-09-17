"""Core vending workflow service."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from .. import models
from ..repositories import InventoryRepository, ProductRepository, SaleRepository
from ..schemas import SaleBase
from .hardware import HardwareError, get_hardware
from .payments import PaymentError, PaymentService


class VendingError(RuntimeError):
    pass


class VendingService:
    def __init__(self, session: Session):
        self.session = session
        self.products = ProductRepository(session)
        self.sales = SaleRepository(session)
        self.inventory = InventoryRepository(session)
        self.hardware = get_hardware()
        self.payments = PaymentService()

    def vend(self, payload: SaleBase) -> models.Sale:
        product = self.products.get(payload.product_id)
        if product is None or not product.is_active:
            raise VendingError("Product unavailable")
        if product.quantity < payload.quantity:
            raise VendingError("Insufficient stock")

        total_cost = Decimal(product.price) * payload.quantity
        try:
            self.payments.authorise(total_cost, payload.amount_paid, payload.payment_method)
        except PaymentError as exc:
            sale = models.Sale(
                product_id=product.id,
                quantity=payload.quantity,
                total_price=total_cost,
                payment_method=payload.payment_method,
                status=models.SaleStatusEnum.FAILED,
                error_message=str(exc),
            )
            return self.sales.record(sale)

        product.quantity -= payload.quantity

        try:
            self.hardware.dispense(product.slot_code, payload.quantity)
        except HardwareError as exc:
            product.quantity += payload.quantity
            sale = models.Sale(
                product_id=product.id,
                quantity=payload.quantity,
                total_price=total_cost,
                payment_method=payload.payment_method,
                status=models.SaleStatusEnum.FAILED,
                error_message=str(exc),
            )
            return self.sales.record(sale)

        sale = models.Sale(
            product_id=product.id,
            quantity=payload.quantity,
            total_price=total_cost,
            payment_method=payload.payment_method,
            status=models.SaleStatusEnum.SUCCESS,
        )
        self.sales.record(sale)
        self.inventory.log_event(
            models.InventoryEvent(product_id=product.id, change=-payload.quantity, reason="sale")
        )
        self.session.flush()
        return sale
