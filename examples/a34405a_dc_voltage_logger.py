"""
Agilent 34405A DC Voltage Logger Example

This example reads DC voltage in auto-range mode every 200ms
and logs the data to Excel files.

Uses the BaseDataLogger template for precise timing and buffered output.

Usage:
    python examples/a34405a_dc_voltage_logger.py [RESOURCE_STRING]

Example:
    # Use default resource string (lab's 34405A)
    python examples/a34405a_dc_voltage_logger.py

    # Or specify custom resource string
    python examples/a34405a_dc_voltage_logger.py "USB0::2391::1560::TW47310002::0::INSTR"

Press Ctrl+C to stop logging.
"""

import sys
import signal

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])

from instruments.base_logger import BaseDataLogger
from instruments.agilent import A34405A


class DCVoltageLogger(BaseDataLogger):
    """DC Voltage logger using Agilent 34405A DMM."""

    def __init__(self, resource_string=None, **kwargs):
        """
        Initialize the DC voltage logger.

        Args:
            resource_string: VISA resource string (None for default)
            **kwargs: Additional arguments for BaseDataLogger
        """
        # Default: 200ms interval, save every 50 measurements
        kwargs.setdefault('measurement_interval', 0.2)
        kwargs.setdefault('save_interval', 50)
        super().__init__(**kwargs)

        self.resource_string = resource_string
        self.dmm = None

    def setup_instrument(self):
        """Connect and configure the DMM."""
        self.dmm = A34405A(self.resource_string)
        self.dmm.connect()

        # Configure for DC voltage measurement in auto-range
        print("Configuring DC voltage measurement (auto-range)...")
        self.dmm.configure_dc_voltage()

        # Set trigger source to immediate for fast continuous readings
        self.dmm.set_trigger_source("IMM")

        print(f"  Mode: DC Voltage (auto-range)")
        print(f"  Trigger: Immediate")

    def read_measurement(self):
        """Read DC voltage from the DMM."""
        try:
            return self.dmm.read()
        except Exception as e:
            print(f"Error reading voltage: {e}")
            return None

    def cleanup_instrument(self):
        """Disconnect from the DMM."""
        if self.dmm:
            self.dmm.disconnect()

    def get_headers(self):
        """Return Excel column headers."""
        return ["Timestamp", "DC Voltage (V)", "Elapsed Time (ms)"]

    def format_display(self, timestamp_str, elapsed_ms, measurement):
        """Format voltage for console display."""
        if measurement is not None:
            return f"{timestamp_str} | {measurement:12.6f} V | {elapsed_ms:10.1f} ms"
        return f"{timestamp_str} | Error | {elapsed_ms:10.1f} ms"


def signal_handler(signum, frame):
    """Handle Ctrl+C signal."""
    print("\n\nReceived interrupt signal. Stopping...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Get resource string from command line or use default
    resource_string = sys.argv[1] if len(sys.argv) >= 2 else None

    if resource_string is None:
        print(f"Using default resource: {A34405A.DEFAULT_RESOURCE}")

    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start logger
    logger = DCVoltageLogger(resource_string)
    logger.start()


if __name__ == "__main__":
    main()
