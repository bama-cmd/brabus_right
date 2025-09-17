# brabus_right
# PiVend — Raspberry Pi Vending Machine Controller

PiVend is a FastAPI-based application designed to run on a Raspberry Pi and manage a smart vending machine. It provides
hardware abstraction for the machine actuators and sensors, inventory and payment handling, and a set of remote
management/analytics APIs.

## Features

- **Hardware abstraction layer** with Raspberry Pi GPIO support and a mock backend for development.
- **Inventory and product management** including restocking and auditing events.
- **Purchase workflow** that validates payments, vends products, and records sales.
- **Telemetry capture** for environmental monitoring (temperature, humidity, door sensor).
- **Analytics endpoints** that surface sales summaries and inventory turnover for remote dashboards.
- **RESTful FastAPI interface** suitable for integration with IoT dashboards or mobile apps.
- **27" portrait kiosk UI simulator** with a guided flow to experience the touch interface.

## Project layout

```
app/
  api/                # FastAPI routers
  services/           # Business logic (hardware, inventory, vending, analytics)
  models.py           # SQLAlchemy ORM models
  database.py         # Engine/session helpers
  schemas.py          # Pydantic request/response models
  main.py             # FastAPI application entry point
requirements.txt      # Python dependencies
```

## Getting started

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment (optional)

Environment variables are prefixed with `PIVEND_`. Useful settings include:

- `PIVEND_DATABASE_URL` — override the default SQLite location (`sqlite:///./data/vending.db`).
- `PIVEND_GPIO_MODE` — set to `real` on Raspberry Pi hardware to enable GPIO access (defaults to `mock`).

### 3. Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

On startup the application creates the SQLite schema under `./data`. The API root is `/api/v1/`.

### 4. Example API usage

- `GET /api/v1/admin/products` — list products and inventory levels.
- `POST /api/v1/admin/products` — create a new product slot.
- `POST /api/v1/vending/purchase` — vend an item (handles payment validation, hardware dispense, and sale recording).
- `POST /api/v1/vending/telemetry/capture` — capture a telemetry sample using the configured hardware backend.
- `GET /api/v1/analytics/sales/summary` — retrieve aggregated sales KPIs.

### 5. Hardware integration notes

- When `PIVEND_GPIO_MODE=real`, the service attempts to use the `RPi.GPIO` library. Ensure the module is installed and
  wiring matches the channel map in `app/services/hardware.py`.
- Environmental sensor handling is abstracted via `TelemetryService`. Replace the placeholder logic with your chosen
  sensor's driver (e.g. DHT22) and adjust error handling as needed.
- The mock hardware backend simulates readings and can be used for development and automated testing.

### 6. Telemetry & analytics

Telemetry records (temperature, humidity, door sensor) are stored in SQLite and can be fetched for dashboards. Sales and
inventory events feed the analytics endpoints that summarise volume, revenue, and product performance.

### 7. Running tests

```bash
pytest
```

The test suite provisions a temporary SQLite database and exercises a full vending flow including purchase,
telemetry capture, and analytics aggregation.

## Touch interface simulator

An interactive prototype of the kiosk interface is available under [`ui/index.html`](ui/index.html). It is optimised
for a 27" portrait display and includes screen-by-screen navigation and an automated guided demo.

### Launch the simulator locally

```bash
cd ui
python -m http.server 8001
# visit http://localhost:8001 in your browser
```

Inside the simulator you can:

- Jump directly to the attract loop, product catalog, cart, payment, dispense, or admin screens.
- Run a guided customer journey that automatically moves through the primary flow.
- Inspect live telemetry and analytics cards that reflect the API's focus on remote operations.

## Deploying on Raspberry Pi

1. Install system dependencies:
   ```bash
   sudo apt update && sudo apt install python3-venv python3-pip
   pip install --upgrade pip
   ```
2. Clone this repository onto the Pi and follow the steps above to install dependencies.
3. Set up a systemd service or process manager (e.g. `pm2`, `supervisor`) to launch Uvicorn on boot.
4. Expose the FastAPI service securely (VPN, reverse proxy with TLS) to access analytics and remote management tools.

## License

MIT License
