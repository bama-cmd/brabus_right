diff --git a//dev/null b/app/api/endpoints/analytics.py
index 0000000000000000000000000000000000000000..69940434a46dc758020312f0436b33bc6e73b019 100644
--- a//dev/null
+++ b/app/api/endpoints/analytics.py
@@ -0,0 +1,33 @@
+"""Endpoints providing analytics and reporting data."""
+
+from __future__ import annotations
+
+from fastapi import APIRouter, Depends
+from sqlalchemy.orm import Session
+
+from ...dependencies import get_db_session
+from ...schemas import InventoryTurnoverResponse, SaleSummary, TelemetryRead
+from ...services.analytics import AnalyticsService
+
+router = APIRouter()
+
+
+@router.get("/sales/summary", response_model=SaleSummary)
+def sales_summary(days: int = 30, session: Session = Depends(get_db_session)):
+    service = AnalyticsService(session)
+    summary = service.sales_summary(days=days)
+    return summary
+
+
+@router.get("/telemetry/trend", response_model=list[TelemetryRead])
+def telemetry_trend(hours: int = 24, session: Session = Depends(get_db_session)):
+    service = AnalyticsService(session)
+    telemetry = service.telemetry_trend(hours=hours)
+    return telemetry
+
+
+@router.get("/inventory/turnover", response_model=InventoryTurnoverResponse)
+def inventory_turnover(days: int = 30, session: Session = Depends(get_db_session)):
+    service = AnalyticsService(session)
+    return service.inventory_turnover(days=days)
+
