"""Administrative routes for managing the vending machine remotely."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...dependencies import get_db_session
from ...schemas import (
    DeviceStateRead,
    DeviceStateUpdate,
    InventoryAdjustment,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from ...services.inventory import InventoryService
from ...services.tasks import DeviceService

router = APIRouter()


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, session: Session = Depends(get_db_session)):
    service = InventoryService(session)
    try:
        product = service.create_product(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return product


@router.get("/products", response_model=list[ProductRead])
def list_products(session: Session = Depends(get_db_session)):
    service = InventoryService(session)
    return service.list_products(active_only=False)


@router.patch("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, payload: ProductUpdate, session: Session = Depends(get_db_session)):
    service = InventoryService(session)
    try:
        product = service.update_product(product_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return product


@router.post("/inventory/adjust", response_model=ProductRead)
def adjust_inventory(payload: InventoryAdjustment, session: Session = Depends(get_db_session)):
    service = InventoryService(session)
    try:
        product = service.adjust_inventory(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return product


@router.get("/device-state", response_model=DeviceStateRead)
def read_device_state(session: Session = Depends(get_db_session)):
    service = DeviceService(session)
    state = service.get_state()
    return state


@router.post("/device-state", response_model=DeviceStateRead)
def update_device_state(payload: DeviceStateUpdate, session: Session = Depends(get_db_session)):
    service = DeviceService(session)
    state = service.set_lock(payload.door_locked)
    return state
