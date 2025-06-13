# pylint: disable = missing-module-docstring, missing-function-docstring

import logging
from logger import CustomFormatter

import keysight as ks
from plotter import plot_collected_data

from dataclass import (
    KeysightConfig,
    Channel,
    TimeUnit,
    Trigger,
    TriggerSource,
    SlopeType,
    VoltageUnit,
    FrequencyUnit,
)

# Create the logger
# call:
# "logger = logging.getLogger(__name__)"
# at the top of your dependency to use the same shared logger instance (shared format)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.INFO, handlers={handler})

# Create channels
# channel2 = Channel(
#     number=1,
#     name="MAX2231",
#     vertical_scale=5,
#     vertical_unit=VoltageUnit.V,
#     offset=10,
#     offset_unit=VoltageUnit.V,
# )

channel3 = Channel(
    number=2,
    name="RECEIVER",
    vertical_scale=30,
    vertical_unit=VoltageUnit.mV,
    offset=30,
    offset_unit=VoltageUnit.mV,
)

channel4 = Channel(
    number=3,
    name="PWM_XIAO",
    vertical_scale=2,
    vertical_unit=VoltageUnit.V,
    offset=3,
    offset_unit=VoltageUnit.V,
)


# Create trigger
trigger = Trigger(
    source=TriggerSource.CHANNEL_3,
    slope=SlopeType.POSITIVE,
    threshold=2,
    threshold_unit=VoltageUnit.V,
)

# Create Keysight configuration
keysight_config = KeysightConfig(
    # channels=[channel2, channel3, channel4],
    channels=[channel3, channel4],
    trigger=trigger,
    frequency=1,
    frequency_unit=FrequencyUnit.MHz,
    horizontal_range=2,
    horizontal_unit=TimeUnit.MS,
)

MEASURES_NAME = [
    "Test without wind",
    "Test with wind",
]
OUTPUT_DIR = "measurements"


def main():
    output_files = []

    device = ks.KeysightDevice(keysight_config)
    device.connect()
    device.setup()

    for name in MEASURES_NAME:
        input(f'Press enter to run next test, named: \n "{name}".')

        device.collect()
        f = device.save_measures(OUTPUT_DIR, name)
        output_files.append(f)

    device.release()

    plot_collected_data(OUTPUT_DIR, output_files, "measurements.html")


if __name__ == "__main__":
    main()
