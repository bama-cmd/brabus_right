"""Aggregate API routes for the application."""

from __future__ import annotations

from fastapi import APIRouter

from .endpoints import admin, analytics, vending

api_router = APIRouter()
api_router.include_router(vending.router, prefix="/vending", tags=["vending"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


__all__ = ["api_router"]
