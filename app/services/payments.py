"""Payment orchestration layer.

In production this module would integrate with a payment gateway.
For the prototype we provide a simple validator that ensures the
paid amount covers the requested purchase."""

from __future__ import annotations

from decimal import Decimal


class PaymentError(RuntimeError):
    pass


class PaymentService:
    def authorise(self, total_cost: Decimal, amount_paid: Decimal, method: str) -> None:
        if amount_paid < total_cost:
            raise PaymentError("Insufficient funds")
        if method.lower() not in {"cash", "card", "mobile"}:
            raise PaymentError(f"Unsupported payment method: {method}")
