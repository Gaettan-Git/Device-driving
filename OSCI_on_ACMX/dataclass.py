from dataclasses import dataclass
import logging
from typing import List, Union
from enum import Enum

logger = logging.getLogger(__name__)

# Constants for allowed values for waveform points
# These values shall match the required frequency (`KeysightConfig.frequency`),
# else a warning will be raised using logger.warning()
ALLOWED_WAVEFORM_POINTS = [
    100,
    250,
    500,
    1000,
    2000,
    5000,
    10000,
    20000,
    50000,
    100000,
    200000,
    500000,
    1000000,
    2000000,
]


class TriggerSource(Enum):
    """Trigger name enumeration."""

    CHANNEL_1 = "CHANnel1"
    CHANNEL_2 = "CHANnel2"
    CHANNEL_3 = "CHANnel3"
    CHANNEL_4 = "CHANnel4"
    EXTERNAL = "EXTernal"


class VoltageUnit(Enum):
    """
    Range unit enumeration.
    Represents channel range in value/div (vertical scale).
    """

    V = 1
    mV = 1e-3


class FrequencyUnit(Enum):
    """
    Frequency unit enumeration.
    Represents channel frequency in Hz (horizontal scale).
    """

    HZ = 1
    KHz = 1e3
    MHz = 1e6


class SlopeType(Enum):
    """Trigger slope enumeration."""

    POSITIVE = "POS"
    NEGATIVE = "NEG"
    ETIHER = "EITH"
    ALTERNATE = "ALT"


class TimeUnit(Enum):
    """
    Time unit enumeration.
    Represents time in seconds.
    """

    S = 1
    MS = 1e-3
    US = 1e-6


@dataclass
class Channel:
    """Represents a measurement channel."""

    number: int
    name: str

    vertical_scale: Union[float | int] = 1
    vertical_unit: VoltageUnit = VoltageUnit.V

    offset: Union[float | int] = 0
    offset_unit: VoltageUnit = VoltageUnit.V

    probe_ratio: Union[float | int] = 1.0

    def __post_init__(self):
        self._validate_types()
        self._validate_values()

    def _validate_types(self):
        if not isinstance(self.number, int):
            raise TypeError("Channel number must be an integer.")
        if not isinstance(self.name, str):
            raise TypeError("Channel name must be a string.")
        if not isinstance(self.vertical_scale, (int, float)):
            raise TypeError("Vertical scale must be a number.")
        if not isinstance(self.vertical_unit, VoltageUnit):
            raise TypeError("Invalid vertical unit.")
        if not isinstance(self.offset, (int, float)):
            raise TypeError("Offset must be a number.")
        if not isinstance(self.offset_unit, VoltageUnit):
            raise TypeError("Invalid offset unit.")
        if not isinstance(self.probe_ratio, (int, float)):
            raise TypeError("Probe ratio must be a number.")

    def _validate_values(self):
        if not 1 <= self.number <= 4:
            raise ValueError("Channel number must be between 1 and 4.")
        if not self.name or len(self.name) >= 10:
            raise ValueError(
                "Name must be a non-empty string with fewer than 10 characters."
            )
        if self.vertical_scale <= 0:
            raise ValueError("Vertical scale must be positive.")
        if abs(self.offset) > 4 * self.vertical_scale:
            raise ValueError("Offset must be within +/- 4*vertical_scale.")
        if not 0.1 <= self.probe_ratio <= 10000:
            raise ValueError("Probe ratio must be between 0.1 and 10000.")


@dataclass
class Trigger:
    """Represents a trigger configuration."""

    source: TriggerSource = TriggerSource.EXTERNAL
    slope: SlopeType = SlopeType.POSITIVE
    threshold: int = 1
    threshold_unit: VoltageUnit = VoltageUnit.V

    def __post_init__(self):
        self._validate_types()
        self._validate_values()

    def _validate_types(self):
        if not isinstance(self.source, TriggerSource):
            raise TypeError("Invalid trigger source.")
        if not isinstance(self.slope, SlopeType):
            raise TypeError("Invalid slope type.")
        if not isinstance(self.threshold, (int, float)):
            raise TypeError("Threshold must be a number.")
        if not isinstance(self.threshold_unit, VoltageUnit):
            raise TypeError("Invalid threshold unit.")

    def _validate_values(self):
        if self.threshold <= 0:
            raise ValueError("Threshold must be positive.")


@dataclass
class KeysightConfig:
    """Top-level configuration for Keysight measurement system."""

    channels: List[Channel]
    trigger: Trigger

    horizontal_range: int = 100
    horizontal_unit: TimeUnit = TimeUnit.MS

    frequency: int = 1
    frequency_unit: FrequencyUnit = FrequencyUnit.HZ

    def __post_init__(self):
        self._validate_types()
        self._validate_values()

        # Compute how many points to extract based on provided time/frequency
        time_range_sec = 10 * self.horizontal_range * self.horizontal_unit.value
        freq_hz = self.frequency * self.frequency_unit.value
        desired_points = int(time_range_sec * freq_hz)

        # Warn if it’s not one of the allowed values
        if desired_points not in ALLOWED_WAVEFORM_POINTS:
            closest_pts = min(
            ALLOWED_WAVEFORM_POINTS,
                key=lambda p: abs(p - desired_points)
            )
            actual_freq = closest_pts / time_range_sec


            logger.critical(
                """Requested number of waveform points (%d) is not in allowed set.
                Number of points will be clamped to closest allowed value: %dpoints, %f """,
                desired_points,
                closest_pts,
                actual_freq
            )

    def _validate_types(self):
        if not isinstance(self.channels, list):
            raise TypeError("Channels must be a list.")
        if not all(isinstance(ch, Channel) for ch in self.channels):
            raise TypeError("All items in channels must be Channel instances.")
        if not isinstance(self.trigger, Trigger):
            raise TypeError("Trigger must be a Trigger instance.")
        if not isinstance(self.horizontal_range, (int, float)):
            raise TypeError("Horizontal range must be a number.")
        if not isinstance(self.horizontal_unit, TimeUnit):
            raise TypeError("Invalid horizontal unit.")
        if not isinstance(self.frequency, (int, float)):
            raise TypeError("Frequency must be a number.")
        if not isinstance(self.frequency_unit, FrequencyUnit):
            raise TypeError("Invalid frequency unit.")

    def _validate_values(self):
        if not self.channels:
            raise ValueError("Channels list must not be empty.")
        if self.frequency <= 0:
            raise ValueError("Frequency must be positive.")
        if self.horizontal_range <= 0:
            raise ValueError("Horizontal range must be positive.")
