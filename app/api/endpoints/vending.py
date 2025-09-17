"""Routes powering the vending workflow exposed to consumers."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...dependencies import get_db_session
from ...schemas import ProductRead, SaleBase, SaleRead, TelemetryRead
from ...services.inventory import InventoryService
from ...services.tasks import TelemetryService
from ...services.vending import VendingError, VendingService

router = APIRouter()


@router.get("/products", response_model=list[ProductRead])
def list_products(active_only: bool = False, session: Session = Depends(get_db_session)):
    service = InventoryService(session)
    return service.list_products(active_only=active_only)


@router.post("/purchase", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def purchase(payload: SaleBase, session: Session = Depends(get_db_session)):
    service = VendingService(session)
    try:
        sale = service.vend(payload)
    except VendingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return sale


@router.post("/telemetry/capture", response_model=TelemetryRead)
def capture_telemetry(session: Session = Depends(get_db_session)):
    telemetry_service = TelemetryService(session)
    telemetry = telemetry_service.capture()
    return telemetry


@router.get("/telemetry", response_model=list[TelemetryRead])
def latest_telemetry(session: Session = Depends(get_db_session), limit: int = 50):
    telemetry_service = TelemetryService(session)
    return telemetry_service.repo.latest(limit=limit)
