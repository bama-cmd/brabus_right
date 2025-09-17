"""Pydantic schemas for API responses and requests."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

from .models import SaleStatusEnum


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slot_code: str = Field(min_length=1, max_length=10)
    price: Decimal = Field(gt=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=120)
    price: Optional[Decimal] = Field(default=None, gt=0)
    is_active: Optional[bool] = None
    quantity: Optional[int] = Field(default=None, ge=0)


class ProductRead(ProductBase, ORMModel):
    id: int
    quantity: int
    created_at: datetime
    updated_at: datetime


class InventoryAdjustment(BaseModel):
    product_id: int
    change: int
    reason: str = Field(min_length=3, max_length=50)


class SaleBase(BaseModel):
    product_id: int
    quantity: PositiveInt
    payment_method: str = Field(min_length=2, max_length=30)
    amount_paid: Decimal = Field(gt=0)

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Quantity must be positive")
        return value


class SaleRead(ORMModel):
    id: int
    product_id: int
    quantity: int
    total_price: Decimal
    payment_method: str
    status: SaleStatusEnum
    error_message: Optional[str]
    created_at: datetime


class SaleSummaryProduct(BaseModel):
    name: str
    sales: int


class SaleSummary(BaseModel):
    total_sales: int
    total_revenue: Decimal
    average_ticket: Decimal
    top_products: list[SaleSummaryProduct]


class TelemetryRead(ORMModel):
    id: int
    temperature_c: float
    humidity: float
    door_open: bool
    created_at: datetime


class TelemetryIn(BaseModel):
    temperature_c: float
    humidity: float
    door_open: bool = False


class DeviceStateRead(ORMModel):
    door_locked: bool
    updated_at: datetime


class DeviceStateUpdate(BaseModel):
    door_locked: bool


class InventoryTurnoverItem(BaseModel):
    name: str
    slot_code: str
    quantity_on_hand: int
    sold_last_period: int
    last_updated: datetime


class InventoryTurnoverResponse(BaseModel):
    as_of: datetime
    products: list[InventoryTurnoverItem]
