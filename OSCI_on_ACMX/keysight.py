"""
Module for managing a Keysight oscilloscope using pyVISA.
Supports configuration, data acquisition, and CSV export.
"""

import logging
import os
import time
import csv
from decimal import Decimal
import pyvisa

from dataclass import KeysightConfig, TimeUnit, TriggerSource

# Constants
MAX_CHANNELS = 4
DEVICE_TIMEOUT = 15000  # ms
DEFAULT_OUTPUT_DIR = "measurements"
DEFAULT_MEAS_NAME = "measure"

# Set up logging
logger = logging.getLogger(__name__)


class KeysightDevice:
    def __init__(self, config: KeysightConfig):
        self.config = config
        self.device = None
        self.waveforms = {}
        
    @staticmethod
    def float_to_nr3(number: float) -> str:
        """Convert float to scientific notation (NR3 format)."""
        return f"{Decimal(number):.1E}"

    def time_to_nr3(self, value: int, time_base: TimeUnit) -> str:
        """Convert time to NR3 format using a time base unit."""
        return self.float_to_nr3(value * time_base.value / 10)

    def _write(self, command: str):
        """Send a command to device."""
        try:
            self.device.write(command)
            logger.debug('Sent: "%s"', command)
        except Exception as e:
            logger.error("Write failed: %s", e)

    def _query(self, command: str) -> str:
        """Send a command to device and return the answer."""
        try:
            answer = self.device.query(command)
            logger.debug('Query: "%s" -> %s', command, answer)
            return answer
        except Exception as e:
            logger.error("Query failed: %s", e)
            return ""

    def _reset_device(self):
        """
        Reset device to it's default state.
        Ensure oscilloscope is in a known state before configuration.
        """
        self._write("*RST")
        self._write("*CLS")
        self._write(":STOP")

        for ch in range(1, MAX_CHANNELS + 1):
            self._write(f":CHANnel{ch}:DISPlay OFF")

        logger.debug("Device reset complete.")

    def _setup_time_base(self):
        """
        Set up time base, in time/division
        Note: Device has 10 horizontal divisions
        """
        scale = self.time_to_nr3(
            self.config.horizontal_range, self.config.horizontal_unit
        )
        self._write(f":TIMebase:SCALe {scale}")
        self._write(":TIMebase:REFerence LEFT")
        self._write(":TIMebase:POSition 0")
        logger.debug("Time base setup done.")

    def _setup_acquisition(self):
        """Set up acquisition mode"""
        self._write(":ACQuire:TYPE NORMal")
        logger.debug("Acquisition setup done.")

    def _setup_external_channel(self):
        trig = self.config.trigger
        if trig.source == TriggerSource.EXTERNAL:
            self._write(":EXTernal:POSition 0")
            self._write(":EXTernal:PROBe X1")
            self._write(f":EXTernal:RANGe {trig.threshold}{trig.threshold_unit.name}")
            logger.debug("External channel setup done.")

    def _setup_channels(self):
        """Set up channels parameters"""
        for ch in self.config.channels:
            self._write(f":CHANnel{ch.number}:COUPling DC")
            self._write(f":CHANnel{ch.number}:UNITs VOLT")

            probe_ratio = self.float_to_nr3(ch.probe_ratio)
            self._write(f":CHANnel{ch.number}:PROBe {probe_ratio}")

            scale_str = self.float_to_nr3(ch.vertical_scale)
            self._write(f":CHANnel{ch.number}:SCALe {scale_str}{ch.vertical_unit.name}")

            offset_str = self.float_to_nr3(ch.offset)
            self._write(f":CHANnel{ch.number}:OFFSet {offset_str}{ch.offset_unit.name}")

            self._write(f":CHANnel{ch.number}:DISPlay ON")
            self._write(f':CHANnel{ch.number}:LABel "{ch.name}"')
            logger.debug(f"Channel{ch.number} setup done.")

        self._write(":DISPlay:LABel ON")

    def _setup_trigger(self):
        """Set up trigger parameters"""
        trig = self.config.trigger
        self._write(":TRIGger:MODE EDGE")
        self._write(f":TRIGger:EDGE:SOURce {trig.source.value}")
        self._write(f":TRIGger:EDGE:SLOPe {trig.slope.value}")
        self._write(f":TRIGger:EDGE:LEVel {self.float_to_nr3(trig.threshold)}")
        logger.debug("Trigger setup done.")

    def _acquire_data(self):
        """Acquire data from device by waiting for trigger event to be detected."""
        try:
            self._write(":WAVeform:FORMat ASCII")
            self._write(":WAVeform:POINts:MODE MAXimum")

            # Calculate the number of points based on the horizontal scale and required frequency
            time_range = (
                10 * self.config.horizontal_range * self.config.horizontal_unit.value
            )
            freq = self.config.frequency * self.config.frequency_unit.value
            num_points = int(time_range * freq)
            self._write(f":WAVeform:POINts {num_points}")

            logger.info("Waiting for trigger")

            self._query("*OPC?")
            self._write(":SINGLE")

            while True:
                cond = int(self._query(":OPERegister:CONDition?"))
                if (cond & 0b1000) == 0:
                    break
                time.sleep(0.001)

            logger.info("Trigger detected")
        except Exception as e:
            logger.error("Acquisition error: %s", e)

    def connect(self, address: str = None):
        """Connect using the provided VISA address."""
        logger.info("Connecting to target device...")
        try:
            rm = pyvisa.ResourceManager()
            if address:
                self.device = rm.open_resource(address)
            else:
                self.device = rm.open_resource(rm.list_resources()[0])
            self.device.timeout = DEVICE_TIMEOUT
            self._reset_device()
            logger.info('Connected to "%s"', address)
        except Exception as e:
            logger.error("Connection failed: %s", e)

    def setup(self):
        """Set up the device with provided configuration."""
        try:
            logger.info("Running setup")
            self._setup_acquisition()
            self._setup_time_base()
            self._setup_external_channel()
            self._setup_channels()
            self._setup_trigger()
            logger.info("Device setup done")
        except KeyboardInterrupt:
            self.release()

    def collect(self):
        """Collect data"""
        try:
            self._acquire_data()
            for ch in self.config.channels:
                logger.info(f'Capturing data from Channel {ch.number} ("{ch.name}")')
                self._write(f":WAVeform:SOURce CHANnel{ch.number}")
                raw_data = self._query(":WAVeform:DATA?").strip()

                try:
                    values = [float(v) for v in raw_data.split(",")[1:]]
                    self.waveforms[ch.name] = values
                    logger.info(f"{ch.name}: {len(values)} points collected")
                except Exception as e:
                    logger.error(f"Failed parsing data for {ch.name}: {e}")
                    self.waveforms[ch.name] = []

            logger.info("Data retrieval done")
        except KeyboardInterrupt:
            self.release()

    def save_measures(self, folder: str, name: str) -> str:
        """
        Save collected data to a CSV file.

        The file is named based on the provided name and saved in the specified folder.
        Folder is created if it does not exist.
        """
        logger.info("Saving captured data...")
        os.makedirs(folder, exist_ok=True)

        safe_name = name.lower().replace(" ", "_").split(".", 1)[0] + ".csv"
        file_path = os.path.join(folder, safe_name)

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["Timestamp"] + [ch.name for ch in self.config.channels]
            writer.writerow(header)

            min_len = min(len(data) for data in self.waveforms.values())
            if min_len == 0:
                logger.error("No data to save")
                return ""

            sampling_duration = (
                self.config.horizontal_range * self.config.horizontal_unit.value
            )
            time_increment = sampling_duration / min_len

            for i in range(min_len - 1):
                time_stamp = i * time_increment
                row = [time_stamp] + [
                    self.waveforms[ch.name][i] for ch in self.config.channels
                ]
                writer.writerow(row)
        logger.info("Data saved to: %s", file_path)
        return safe_name

    def release(self):
        """Release the device connection."""
        logger.info("Releasing device connection")
        if self.device:
            self.device.close()
            logger.info("Device released")
