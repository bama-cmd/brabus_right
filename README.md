# Brabus Right Vending Machine (Simplified)

This project provides a deliberately small FastAPI-compatible backend that simulates a Raspberry Pi powered vending machine.  The real codebase depends on several third-party packages, but for the purposes of this kata the application is implemented with an in-repo FastAPI shim and an in-memory data store so it can run in a restricted environment with no network access.

## Features

* Create and list vending products.
* Simulate purchases with payment validation and inventory adjustments.
* Capture deterministic telemetry readings and query recent trends.
* Produce sales summaries and inventory turnover analytics.

All data lives in memory for the lifetime of the application instance, which keeps the tests deterministic and removes the need for a database.

## Running the tests

No external dependencies are required.  From the repository root simply execute:

```bash
python -m pytest
```

The included tests drive the full API flow by talking to the FastAPI shim.

## Starting the application manually

Although the shim is not a full ASGI implementation, you can still interact with the API objects directly:

```python
from app.main import create_app

app = create_app()
status, payload = app.handle_request("POST", "/api/v1/admin/products", json={
    "name": "Soda",
    "slot_code": "A1",
    "price": "2.50",
    "quantity": 5,
    "is_active": True,
})
print(status)   # 201
print(payload)
```

For production usage you should replace the shim with the real FastAPI dependency and persist data in an actual database.  The simplified implementation here is designed to make it easy to run in offline grading environments.
