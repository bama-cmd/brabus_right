"""Hardware abstraction to interact with vending machine peripherals."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from time import sleep
from typing import Protocol

from ..config import settings

logger = logging.getLogger(__name__)


class HardwareError(RuntimeError):
    """Raised when hardware operations fail."""


class HardwareInterface(Protocol):
    def dispense(self, slot_code: str, quantity: int) -> None:
        """Trigger the actuator to vend a product."""

    def read_temperature(self) -> float:
        """Return the internal temperature in Celsius."""

    def read_humidity(self) -> float:
        """Return the relative humidity percentage."""

    def is_door_open(self) -> bool:
        """Check the status of the maintenance door sensor."""

    def set_door_lock(self, locked: bool) -> None:
        """Lock or unlock the maintenance door."""


_hardware_instance: HardwareInterface | None = None


@dataclass
class HardwareCapabilities:
    supports_door_lock: bool = True
    supports_environmental_sensors: bool = True


class MockHardware:
    """Fallback hardware layer used for development and automated tests."""

    capabilities = HardwareCapabilities()

    def __init__(self) -> None:
        self.door_locked = True

    def dispense(self, slot_code: str, quantity: int) -> None:
        logger.info("Dispensing %s item(s) from slot %s", quantity, slot_code)
        if quantity <= 0:
            raise HardwareError("Quantity must be positive")
        sleep(0.1)

    def read_temperature(self) -> float:
        return round(random.uniform(3.5, 6.5), 2)

    def read_humidity(self) -> float:
        return round(random.uniform(25, 60), 2)

    def is_door_open(self) -> bool:
        return not self.door_locked and random.random() < 0.1

    def set_door_lock(self, locked: bool) -> None:
        logger.info("Setting mock door lock to %s", locked)
        self.door_locked = locked


class GPIOHardware:
    """Concrete hardware implementation for Raspberry Pi deployments."""

    capabilities = HardwareCapabilities()

    def __init__(self) -> None:
        try:
            import RPi.GPIO as GPIO  # type: ignore
        except ImportError as exc:  # pragma: no cover - executed on non-Pi machines
            raise HardwareError("RPi.GPIO package is required for real hardware mode") from exc

        self.GPIO = GPIO
        GPIO.setmode(GPIO.BCM)
        # Example channel mapping. Should be adapted for actual wiring.
        self.slot_channels = {
            "A1": 2,
            "A2": 3,
            "B1": 4,
            "B2": 17,
        }
        self.door_sensor_channel = 27
        self.lock_relay_channel = 22
        GPIO.setup(list(self.slot_channels.values()), GPIO.OUT)
        GPIO.setup(self.door_sensor_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.lock_relay_channel, GPIO.OUT)
        GPIO.output(self.lock_relay_channel, GPIO.HIGH)

        # Optional: environment sensors (e.g., DHT22) would be initialised here.
        self.sensor = None

    def dispense(self, slot_code: str, quantity: int) -> None:
        channel = self.slot_channels.get(slot_code)
        if channel is None:
            raise HardwareError(f"Unknown slot {slot_code}")
        for _ in range(quantity):
            self.GPIO.output(channel, self.GPIO.HIGH)
            sleep(0.5)
            self.GPIO.output(channel, self.GPIO.LOW)
            sleep(0.1)

    def read_temperature(self) -> float:
        if self.sensor is None:
            raise HardwareError("Temperature sensor not configured")
        temperature, _humidity = self.sensor.read()
        return float(temperature)

    def read_humidity(self) -> float:
        if self.sensor is None:
            raise HardwareError("Humidity sensor not configured")
        _temperature, humidity = self.sensor.read()
        return float(humidity)

    def is_door_open(self) -> bool:
        return bool(self.GPIO.input(self.door_sensor_channel) == self.GPIO.LOW)

    def set_door_lock(self, locked: bool) -> None:
        self.GPIO.output(self.lock_relay_channel, self.GPIO.HIGH if locked else self.GPIO.LOW)


def get_hardware() -> HardwareInterface:
    """Return the configured hardware backend."""

    global _hardware_instance
    if _hardware_instance is None:
        if settings.gpio_mode.lower() == "real":
            try:
                _hardware_instance = GPIOHardware()
            except HardwareError as exc:
                logger.warning("Falling back to mock hardware: %s", exc)
                _hardware_instance = MockHardware()
        else:
            _hardware_instance = MockHardware()
    return _hardware_instance
