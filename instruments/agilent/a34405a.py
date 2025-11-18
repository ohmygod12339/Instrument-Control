"""
Agilent 34405A Digital Multimeter Control Module

This module provides a Python class for controlling the Agilent 34405A
5½ Digit Digital Multimeter via VISA (USB only).

The 34405A is a 5.5 digit bench/system DMM with:
- DC/AC Voltage measurement
- DC/AC Current measurement
- 2-wire and 4-wire Resistance measurement
- Frequency measurement
- Continuity and Diode test

References:
    - Agilent 34405A User's and Service Guide
    - Agilent 34405A Programmer's Reference
"""

import pyvisa
from typing import Optional, Tuple
import time


class A34405A:
    """
    Agilent 34405A Digital Multimeter Control Class

    This class provides methods to control and acquire measurements from an
    Agilent 34405A digital multimeter using SCPI commands over VISA.

    Attributes:
        resource_string (str): VISA resource string for the instrument
        instrument: PyVISA instrument resource
        timeout (int): Command timeout in milliseconds

    Example:
        >>> # Connect using default resource string
        >>> dmm = A34405A()
        >>> dmm.connect()
        >>>
        >>> # Or connect with custom resource string
        >>> dmm = A34405A("USB0::0x0957::0x0618::MY12345678::INSTR")
        >>> dmm.connect()
        >>> print(dmm.identify())
        >>>
        >>> # Measure DC voltage
        >>> voltage = dmm.measure_dc_voltage()
        >>> print(f"DC Voltage: {voltage} V")
        >>>
        >>> # Disconnect
        >>> dmm.disconnect()
    """

    # Default VISA resource string for lab instrument
    DEFAULT_RESOURCE = "USB0::2391::1560::TW47310002::0::INSTR"

    def __init__(self, resource_string: Optional[str] = None, timeout: int = 5000):
        """
        Initialize the 34405A multimeter interface.

        Args:
            resource_string: VISA resource string (default: DEFAULT_RESOURCE)
                USB format: "USB0::0x0957::0x0618::MY########::INSTR"
                If None, uses the lab's default instrument
            timeout: Command timeout in milliseconds (default: 5000)
        """
        self.resource_string = resource_string or self.DEFAULT_RESOURCE
        self.timeout = timeout
        self.instrument = None
        self._rm = None

    def connect(self) -> None:
        """
        Establish connection to the multimeter.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._rm = pyvisa.ResourceManager('@py')  # Use pyvisa-py backend
            self.instrument = self._rm.open_resource(self.resource_string)
            self.instrument.timeout = self.timeout

            # Clear status and reset error queue
            self.write("*CLS")

            print(f"Connected to: {self.identify()}")

        except Exception as e:
            raise ConnectionError(f"Failed to connect to instrument: {e}")

    def disconnect(self) -> None:
        """Close the connection to the multimeter."""
        if self.instrument:
            self.instrument.close()
            self.instrument = None
        if self._rm:
            self._rm.close()
            self._rm = None
        print("Disconnected from multimeter")

    def write(self, command: str) -> None:
        """
        Write a SCPI command to the instrument.

        Args:
            command: SCPI command string

        Raises:
            RuntimeError: If not connected
        """
        if not self.instrument:
            raise RuntimeError("Not connected to instrument. Call connect() first.")
        self.instrument.write(command)

    def query(self, command: str) -> str:
        """
        Query the instrument and return the response.

        Args:
            command: SCPI query command string

        Returns:
            Response string from instrument

        Raises:
            RuntimeError: If not connected
        """
        if not self.instrument:
            raise RuntimeError("Not connected to instrument. Call connect() first.")
        return self.instrument.query(command).strip()

    # ========== Instrument Identification ==========

    def identify(self) -> str:
        """
        Query instrument identification.

        Returns:
            Identification string (Manufacturer, Model, Serial, Firmware)
        """
        return self.query("*IDN?")

    def reset(self) -> None:
        """Reset the instrument to default settings."""
        self.write("*RST")
        time.sleep(1)  # Wait for reset to complete

    def clear_status(self) -> None:
        """Clear the status registers and error queue."""
        self.write("*CLS")

    def get_error(self) -> str:
        """
        Read and return the oldest error from the error queue.

        Returns:
            Error string (format: "code,description")
        """
        return self.query(":SYST:ERR?")

    # ========== DC Voltage Measurements ==========

    def measure_dc_voltage(self, range_val: Optional[float] = None,
                          resolution: Optional[float] = None) -> float:
        """
        Measure DC voltage.

        Args:
            range_val: Measurement range in volts (None for auto-range)
                      Valid ranges: 0.1, 1, 10, 100, 1000
            resolution: Measurement resolution in volts (None for default)

        Returns:
            DC voltage in volts
        """
        if range_val is None and resolution is None:
            return float(self.query(":MEAS:VOLT:DC?"))
        elif resolution is None:
            return float(self.query(f":MEAS:VOLT:DC? {range_val}"))
        else:
            return float(self.query(f":MEAS:VOLT:DC? {range_val},{resolution}"))

    def configure_dc_voltage(self, range_val: Optional[float] = None,
                            resolution: Optional[float] = None) -> None:
        """
        Configure DC voltage measurement without triggering.

        Args:
            range_val: Measurement range in volts (None for auto-range)
            resolution: Measurement resolution in volts
        """
        if range_val is None:
            self.write(":CONF:VOLT:DC")
        elif resolution is None:
            self.write(f":CONF:VOLT:DC {range_val}")
        else:
            self.write(f":CONF:VOLT:DC {range_val},{resolution}")

    # ========== AC Voltage Measurements ==========

    def measure_ac_voltage(self, range_val: Optional[float] = None,
                          resolution: Optional[float] = None) -> float:
        """
        Measure AC voltage (RMS).

        Args:
            range_val: Measurement range in volts (None for auto-range)
                      Valid ranges: 0.1, 1, 10, 100, 750
            resolution: Measurement resolution in volts

        Returns:
            AC voltage in volts (RMS)
        """
        if range_val is None and resolution is None:
            return float(self.query(":MEAS:VOLT:AC?"))
        elif resolution is None:
            return float(self.query(f":MEAS:VOLT:AC? {range_val}"))
        else:
            return float(self.query(f":MEAS:VOLT:AC? {range_val},{resolution}"))

    def configure_ac_voltage(self, range_val: Optional[float] = None,
                            resolution: Optional[float] = None) -> None:
        """
        Configure AC voltage measurement without triggering.

        Args:
            range_val: Measurement range in volts
            resolution: Measurement resolution in volts
        """
        if range_val is None:
            self.write(":CONF:VOLT:AC")
        elif resolution is None:
            self.write(f":CONF:VOLT:AC {range_val}")
        else:
            self.write(f":CONF:VOLT:AC {range_val},{resolution}")

    # ========== DC Current Measurements ==========

    def measure_dc_current(self, range_val: Optional[float] = None,
                          resolution: Optional[float] = None) -> float:
        """
        Measure DC current.

        Args:
            range_val: Measurement range in amps (None for auto-range)
                      Valid ranges: 0.0001, 0.001, 0.01, 0.1, 1, 3
            resolution: Measurement resolution in amps

        Returns:
            DC current in amps
        """
        if range_val is None and resolution is None:
            return float(self.query(":MEAS:CURR:DC?"))
        elif resolution is None:
            return float(self.query(f":MEAS:CURR:DC? {range_val}"))
        else:
            return float(self.query(f":MEAS:CURR:DC? {range_val},{resolution}"))

    def configure_dc_current(self, range_val: Optional[float] = None,
                            resolution: Optional[float] = None) -> None:
        """
        Configure DC current measurement without triggering.

        Args:
            range_val: Measurement range in amps
            resolution: Measurement resolution in amps
        """
        if range_val is None:
            self.write(":CONF:CURR:DC")
        elif resolution is None:
            self.write(f":CONF:CURR:DC {range_val}")
        else:
            self.write(f":CONF:CURR:DC {range_val},{resolution}")

    # ========== AC Current Measurements ==========

    def measure_ac_current(self, range_val: Optional[float] = None,
                          resolution: Optional[float] = None) -> float:
        """
        Measure AC current (RMS).

        Args:
            range_val: Measurement range in amps (None for auto-range)
                      Valid ranges: 0.001, 0.01, 0.1, 1, 3
            resolution: Measurement resolution in amps

        Returns:
            AC current in amps (RMS)
        """
        if range_val is None and resolution is None:
            return float(self.query(":MEAS:CURR:AC?"))
        elif resolution is None:
            return float(self.query(f":MEAS:CURR:AC? {range_val}"))
        else:
            return float(self.query(f":MEAS:CURR:AC? {range_val},{resolution}"))

    def configure_ac_current(self, range_val: Optional[float] = None,
                            resolution: Optional[float] = None) -> None:
        """
        Configure AC current measurement without triggering.

        Args:
            range_val: Measurement range in amps
            resolution: Measurement resolution in amps
        """
        if range_val is None:
            self.write(":CONF:CURR:AC")
        elif resolution is None:
            self.write(f":CONF:CURR:AC {range_val}")
        else:
            self.write(f":CONF:CURR:AC {range_val},{resolution}")

    # ========== Resistance Measurements ==========

    def measure_resistance(self, range_val: Optional[float] = None,
                          resolution: Optional[float] = None) -> float:
        """
        Measure 2-wire resistance.

        Args:
            range_val: Measurement range in ohms (None for auto-range)
                      Valid ranges: 100, 1000, 10000, 100000, 1000000, 10000000, 100000000
            resolution: Measurement resolution in ohms

        Returns:
            Resistance in ohms
        """
        if range_val is None and resolution is None:
            return float(self.query(":MEAS:RES?"))
        elif resolution is None:
            return float(self.query(f":MEAS:RES? {range_val}"))
        else:
            return float(self.query(f":MEAS:RES? {range_val},{resolution}"))

    def configure_resistance(self, range_val: Optional[float] = None,
                            resolution: Optional[float] = None) -> None:
        """
        Configure 2-wire resistance measurement without triggering.

        Args:
            range_val: Measurement range in ohms
            resolution: Measurement resolution in ohms
        """
        if range_val is None:
            self.write(":CONF:RES")
        elif resolution is None:
            self.write(f":CONF:RES {range_val}")
        else:
            self.write(f":CONF:RES {range_val},{resolution}")

    def measure_resistance_4wire(self, range_val: Optional[float] = None,
                                resolution: Optional[float] = None) -> float:
        """
        Measure 4-wire resistance.

        Args:
            range_val: Measurement range in ohms (None for auto-range)
            resolution: Measurement resolution in ohms

        Returns:
            Resistance in ohms
        """
        if range_val is None and resolution is None:
            return float(self.query(":MEAS:FRES?"))
        elif resolution is None:
            return float(self.query(f":MEAS:FRES? {range_val}"))
        else:
            return float(self.query(f":MEAS:FRES? {range_val},{resolution}"))

    def configure_resistance_4wire(self, range_val: Optional[float] = None,
                                  resolution: Optional[float] = None) -> None:
        """
        Configure 4-wire resistance measurement without triggering.

        Args:
            range_val: Measurement range in ohms
            resolution: Measurement resolution in ohms
        """
        if range_val is None:
            self.write(":CONF:FRES")
        elif resolution is None:
            self.write(f":CONF:FRES {range_val}")
        else:
            self.write(f":CONF:FRES {range_val},{resolution}")

    # ========== Frequency Measurements ==========

    def measure_frequency(self, range_val: Optional[float] = None,
                         resolution: Optional[float] = None) -> float:
        """
        Measure frequency.

        Args:
            range_val: Expected voltage range in volts (None for auto-range)
            resolution: Measurement resolution in Hz

        Returns:
            Frequency in Hz
        """
        if range_val is None and resolution is None:
            return float(self.query(":MEAS:FREQ?"))
        elif resolution is None:
            return float(self.query(f":MEAS:FREQ? {range_val}"))
        else:
            return float(self.query(f":MEAS:FREQ? {range_val},{resolution}"))

    def configure_frequency(self, range_val: Optional[float] = None,
                           resolution: Optional[float] = None) -> None:
        """
        Configure frequency measurement without triggering.

        Args:
            range_val: Expected voltage range in volts
            resolution: Measurement resolution in Hz
        """
        if range_val is None:
            self.write(":CONF:FREQ")
        elif resolution is None:
            self.write(f":CONF:FREQ {range_val}")
        else:
            self.write(f":CONF:FREQ {range_val},{resolution}")

    # ========== Continuity and Diode ==========

    def measure_continuity(self) -> float:
        """
        Measure continuity (resistance with beeper).

        Returns:
            Resistance in ohms
        """
        return float(self.query(":MEAS:CONT?"))

    def configure_continuity(self) -> None:
        """Configure continuity measurement without triggering."""
        self.write(":CONF:CONT")

    def measure_diode(self) -> float:
        """
        Measure diode forward voltage.

        Returns:
            Forward voltage in volts
        """
        return float(self.query(":MEAS:DIOD?"))

    def configure_diode(self) -> None:
        """Configure diode test without triggering."""
        self.write(":CONF:DIOD")

    # ========== Trigger and Read ==========

    def read(self) -> float:
        """
        Trigger a measurement and read the result.

        Uses the currently configured measurement function.

        Returns:
            Measurement value
        """
        return float(self.query(":READ?"))

    def initiate(self) -> None:
        """Initiate a measurement (trigger)."""
        self.write(":INIT")

    def fetch(self) -> float:
        """
        Fetch the last measurement result.

        Returns:
            Last measurement value
        """
        return float(self.query(":FETC?"))

    def set_trigger_source(self, source: str) -> None:
        """
        Set the trigger source.

        Args:
            source: Trigger source ('IMM', 'BUS', 'EXT')
        """
        source = source.upper()
        if source not in ['IMM', 'BUS', 'EXT']:
            raise ValueError("Trigger source must be 'IMM', 'BUS', or 'EXT'")
        self.write(f":TRIG:SOUR {source}")

    def get_trigger_source(self) -> str:
        """
        Get the trigger source.

        Returns:
            Current trigger source
        """
        return self.query(":TRIG:SOUR?")

    # ========== Sample and Trigger Count ==========

    def set_sample_count(self, count: int) -> None:
        """
        Set the number of samples per trigger.

        Args:
            count: Number of samples (1 to 50000)
        """
        if not 1 <= count <= 50000:
            raise ValueError("Sample count must be between 1 and 50000")
        self.write(f":SAMP:COUN {count}")

    def get_sample_count(self) -> int:
        """
        Get the number of samples per trigger.

        Returns:
            Number of samples
        """
        return int(self.query(":SAMP:COUN?"))

    def set_trigger_count(self, count: int) -> None:
        """
        Set the number of triggers.

        Args:
            count: Number of triggers (1 to 50000)
        """
        if not 1 <= count <= 50000:
            raise ValueError("Trigger count must be between 1 and 50000")
        self.write(f":TRIG:COUN {count}")

    def get_trigger_count(self) -> int:
        """
        Get the number of triggers.

        Returns:
            Number of triggers
        """
        return int(self.query(":TRIG:COUN?"))

    # ========== Display Control ==========

    def display_on(self) -> None:
        """Turn on the display."""
        self.write(":DISP ON")

    def display_off(self) -> None:
        """Turn off the display (faster measurements)."""
        self.write(":DISP OFF")

    def display_text(self, text: str) -> None:
        """
        Display custom text on the DMM screen.

        Args:
            text: Text to display (max 12 characters)
        """
        self.write(f':DISP:TEXT "{text[:12]}"')

    def display_clear_text(self) -> None:
        """Clear custom text from display."""
        self.write(":DISP:TEXT:CLE")

    # ========== Auto-zero and NPLC ==========

    def set_autozero(self, enable: bool) -> None:
        """
        Enable or disable auto-zero.

        Args:
            enable: True to enable, False to disable
        """
        state = "ON" if enable else "OFF"
        self.write(f":ZERO:AUTO {state}")

    def get_autozero(self) -> bool:
        """
        Get auto-zero state.

        Returns:
            True if enabled, False if disabled
        """
        return self.query(":ZERO:AUTO?") == "1"

    def set_nplc(self, nplc: float) -> None:
        """
        Set the integration time in power line cycles (NPLC).

        Args:
            nplc: Number of power line cycles (0.02, 0.2, 1, 10, 100)
                  Higher NPLC = better resolution but slower
        """
        valid_nplc = [0.02, 0.2, 1, 10, 100]
        if nplc not in valid_nplc:
            raise ValueError(f"NPLC must be one of {valid_nplc}")
        self.write(f":VOLT:DC:NPLC {nplc}")

    def get_nplc(self) -> float:
        """
        Get the current NPLC setting.

        Returns:
            Number of power line cycles
        """
        return float(self.query(":VOLT:DC:NPLC?"))

    # ========== Utility Methods ==========

    def beep(self) -> None:
        """Generate a beep from the instrument."""
        self.write(":SYST:BEEP")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __repr__(self) -> str:
        """String representation."""
        connected = "connected" if self.instrument else "disconnected"
        return f"A34405A({self.resource_string}, {connected})"
