"""Virtual IoT sensor.

Simulates a connected environmental sensor (e.g. an ESP32 reading a DHT22 +
air-quality module). Produces realistic temperature, humidity and air-quality
values with natural drift and noise, and occasionally injects an anomaly so the
AI detector has something to catch.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, asdict


# Normal operating baselines for an indoor room.
BASE_TEMP = 22.0      # degrees Celsius
BASE_HUMIDITY = 45.0  # percent
BASE_AQI = 40.0       # air quality index (lower is better)


@dataclass
class Reading:
    timestamp: float
    temperature: float
    humidity: float
    aqi: float

    def to_dict(self) -> dict:
        return asdict(self)


class SensorSimulator:
    """Generates a continuous stream of plausible sensor readings."""

    def __init__(self, anomaly_chance: float = 0.07) -> None:
        self.anomaly_chance = anomaly_chance
        self._t = 0.0  # internal clock used to create slow, smooth drift

    def _drift(self, amplitude: float, period: float) -> float:
        """A slow sine wave so values wander naturally instead of jumping."""
        return amplitude * math.sin(self._t / period)

    def next_reading(self) -> tuple[Reading, bool]:
        """Return the next reading and whether an anomaly was injected."""
        self._t += 1.0

        temperature = BASE_TEMP + self._drift(1.5, 12) + random.gauss(0, 0.3)
        humidity = BASE_HUMIDITY + self._drift(6, 20) + random.gauss(0, 1.0)
        aqi = BASE_AQI + self._drift(8, 16) + random.gauss(0, 2.0)

        injected = False
        if random.random() < self.anomaly_chance:
            injected = True
            kind = random.choice(["heat", "humid", "pollution"])
            if kind == "heat":
                temperature += random.uniform(8, 14)
            elif kind == "humid":
                humidity += random.uniform(25, 40)
            else:
                aqi += random.uniform(80, 160)

        reading = Reading(
            timestamp=time.time(),
            temperature=round(temperature, 2),
            humidity=round(max(0.0, min(100.0, humidity)), 2),
            aqi=round(max(0.0, aqi), 2),
        )
        return reading, injected
