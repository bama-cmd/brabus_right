"""Background style tasks that can be triggered manually or via scheduler."""

from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models
from ..repositories import DeviceStateRepository, TelemetryRepository
from .hardware import HardwareError, get_hardware


class DeviceService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = DeviceStateRepository(session)
        self.hardware = get_hardware()

    def set_lock(self, locked: bool) -> models.DeviceState:
        self.hardware.set_door_lock(locked)
        return self.repo.update(locked)

    def get_state(self) -> models.DeviceState:
        return self.repo.get_or_create()


class TelemetryService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = TelemetryRepository(session)
        self.hardware = get_hardware()

    def capture(self) -> models.Telemetry:
        try:
            temperature = self.hardware.read_temperature()
            humidity = self.hardware.read_humidity()
        except HardwareError:
            # Gracefully handle missing sensors by using placeholder values.
            temperature = 0.0
            humidity = 0.0
        door_open = self.hardware.is_door_open()
        telemetry = models.Telemetry(temperature_c=temperature, humidity=humidity, door_open=door_open)
        return self.repo.log(telemetry)
