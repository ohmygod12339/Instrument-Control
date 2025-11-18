"""
Keysight DSOX4034A Oscilloscope Control Module

This module provides a Python class for controlling the Keysight DSOX4034A
InfiniiVision 4000 X-Series Digital Oscilloscope via VISA (USB or Ethernet).

The DSOX4034A is a 4-channel, 350 MHz, 5 GSa/s oscilloscope.

References:
    - Keysight InfiniiVision 4000 X-Series Programmer's Guide
    - https://www.keysight.com/us/en/assets/9018-06976/programming-guides/9018-06976.pdf
"""

import pyvisa
import numpy as np
from typing import Optional, List, Tuple, Union
import time


class DSOX4034A:
    """
    Keysight DSOX4034A Oscilloscope Control Class

    This class provides methods to control and acquire data from a Keysight DSOX4034A
    oscilloscope using SCPI commands over VISA.

    Attributes:
        resource_string (str): VISA resource string for the instrument
        instrument: PyVISA instrument resource
        timeout (int): Command timeout in milliseconds

    Example:
        >>> # Connect using default resource string
        >>> scope = DSOX4034A()
        >>> scope.connect()
        >>>
        >>> # Or connect via USB
        >>> scope = DSOX4034A("USB0::0x0957::0x17A6::MY########::INSTR")
        >>>
        >>> # Or connect via Ethernet
        >>> scope = DSOX4034A("TCPIP0::192.168.1.100::INSTR")
        >>>
        >>> # Connect and identify
        >>> scope.connect()
        >>> print(scope.identify())
        >>>
        >>> # Auto-scale and acquire waveform
        >>> scope.autoscale()
        >>> waveform = scope.get_waveform(channel=1)
        >>>
        >>> # Disconnect
        >>> scope.disconnect()
    """

    # Default VISA resource string for lab instrument
    DEFAULT_RESOURCE = "TCPIP::192.168.2.60::INSTR"

    # Channel mapping
    CHANNELS = {1: "CHAN1", 2: "CHAN2", 3: "CHAN3", 4: "CHAN4"}

    def __init__(self, resource_string: Optional[str] = None, timeout: int = 5000):
        """
        Initialize the DSOX4034A oscilloscope interface.

        Args:
            resource_string: VISA resource string (default: DEFAULT_RESOURCE)
                USB format: "USB0::0x0957::0x17A6::MY########::INSTR"
                TCPIP format: "TCPIP0::192.168.1.100::INSTR"
                If None, uses the lab's default instrument
            timeout: Command timeout in milliseconds (default: 5000)
        """
        self.resource_string = resource_string or self.DEFAULT_RESOURCE
        self.timeout = timeout
        self.instrument = None
        self._rm = None

    def connect(self) -> None:
        """
        Establish connection to the oscilloscope.

        Raises:
            pyvisa.errors.VisaIOError: If connection fails
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
        """Close the connection to the oscilloscope."""
        if self.instrument:
            self.instrument.close()
            self.instrument = None
        if self._rm:
            self._rm.close()
            self._rm = None
        print("Disconnected from oscilloscope")

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

    def query_binary_values(self, command: str, datatype='B', container=list):
        """
        Query binary data from the instrument.

        Args:
            command: SCPI query command
            datatype: Data type format (default: 'B' for unsigned byte)
            container: Container type for returned data (default: list)

        Returns:
            Binary data in specified container format
        """
        if not self.instrument:
            raise RuntimeError("Not connected to instrument. Call connect() first.")
        return self.instrument.query_binary_values(command, datatype=datatype, container=container)

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
        time.sleep(2)  # Wait for reset to complete

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

    # ========== Display and System Functions ==========

    def autoscale(self) -> None:
        """Perform autoscale on all active channels."""
        self.write(":AUT")
        time.sleep(2)  # Wait for autoscale to complete

    def run(self) -> None:
        """Start the oscilloscope acquisition."""
        self.write(":RUN")

    def stop(self) -> None:
        """Stop the oscilloscope acquisition."""
        self.write(":STOP")

    def single(self) -> None:
        """Set oscilloscope to single trigger mode."""
        self.write(":SING")

    def digitize(self, channels: Optional[List[int]] = None) -> None:
        """
        Acquire waveform data (similar to pressing Single button).

        Args:
            channels: List of channel numbers to digitize (e.g., [1, 2])
                     If None, digitizes all active channels
        """
        if channels:
            chan_str = ",".join([self.CHANNELS[ch] for ch in channels])
            self.write(f":DIG {chan_str}")
        else:
            self.write(":DIG")

    # ========== Channel Configuration ==========

    def channel_on(self, channel: int) -> None:
        """
        Turn on a channel display.

        Args:
            channel: Channel number (1-4)
        """
        self._validate_channel(channel)
        self.write(f":{self.CHANNELS[channel]}:DISP ON")

    def channel_off(self, channel: int) -> None:
        """
        Turn off a channel display.

        Args:
            channel: Channel number (1-4)
        """
        self._validate_channel(channel)
        self.write(f":{self.CHANNELS[channel]}:DISP OFF")

    def is_channel_on(self, channel: int) -> bool:
        """
        Check if a channel is displayed.

        Args:
            channel: Channel number (1-4)

        Returns:
            True if channel is on, False otherwise
        """
        self._validate_channel(channel)
        result = self.query(f":{self.CHANNELS[channel]}:DISP?")
        return result == "1"

    def set_channel_scale(self, channel: int, scale: float) -> None:
        """
        Set the vertical scale (volts/division) for a channel.

        Args:
            channel: Channel number (1-4)
            scale: Vertical scale in volts/division
        """
        self._validate_channel(channel)
        self.write(f":{self.CHANNELS[channel]}:SCAL {scale}")

    def get_channel_scale(self, channel: int) -> float:
        """
        Get the vertical scale for a channel.

        Args:
            channel: Channel number (1-4)

        Returns:
            Vertical scale in volts/division
        """
        self._validate_channel(channel)
        return float(self.query(f":{self.CHANNELS[channel]}:SCAL?"))

    def set_channel_offset(self, channel: int, offset: float) -> None:
        """
        Set the vertical offset for a channel.

        Args:
            channel: Channel number (1-4)
            offset: Vertical offset in volts
        """
        self._validate_channel(channel)
        self.write(f":{self.CHANNELS[channel]}:OFFS {offset}")

    def get_channel_offset(self, channel: int) -> float:
        """
        Get the vertical offset for a channel.

        Args:
            channel: Channel number (1-4)

        Returns:
            Vertical offset in volts
        """
        self._validate_channel(channel)
        return float(self.query(f":{self.CHANNELS[channel]}:OFFS?"))

    def set_channel_coupling(self, channel: int, coupling: str) -> None:
        """
        Set the input coupling for a channel.

        Args:
            channel: Channel number (1-4)
            coupling: Coupling type ('AC', 'DC')
        """
        self._validate_channel(channel)
        coupling = coupling.upper()
        if coupling not in ['AC', 'DC']:
            raise ValueError("Coupling must be 'AC' or 'DC'")
        self.write(f":{self.CHANNELS[channel]}:COUP {coupling}")

    def get_channel_coupling(self, channel: int) -> str:
        """
        Get the input coupling for a channel.

        Args:
            channel: Channel number (1-4)

        Returns:
            Coupling type ('AC' or 'DC')
        """
        self._validate_channel(channel)
        return self.query(f":{self.CHANNELS[channel]}:COUP?")

    # ========== Timebase Configuration ==========

    def set_timebase_scale(self, scale: float) -> None:
        """
        Set the horizontal timebase scale (seconds/division).

        Args:
            scale: Time per division in seconds
        """
        self.write(f":TIM:SCAL {scale}")

    def get_timebase_scale(self) -> float:
        """
        Get the horizontal timebase scale.

        Returns:
            Time per division in seconds
        """
        return float(self.query(":TIM:SCAL?"))

    def set_timebase_position(self, position: float) -> None:
        """
        Set the horizontal position (delay).

        Args:
            position: Time position in seconds
        """
        self.write(f":TIM:POS {position}")

    def get_timebase_position(self) -> float:
        """
        Get the horizontal position.

        Returns:
            Time position in seconds
        """
        return float(self.query(":TIM:POS?"))

    # ========== Trigger Configuration ==========

    def set_trigger_mode(self, mode: str) -> None:
        """
        Set the trigger mode.

        Args:
            mode: Trigger mode ('EDGE', 'GLIT', 'PATT', etc.)
        """
        self.write(f":TRIG:MODE {mode}")

    def get_trigger_mode(self) -> str:
        """
        Get the trigger mode.

        Returns:
            Current trigger mode
        """
        return self.query(":TRIG:MODE?")

    def set_trigger_source(self, source: Union[int, str]) -> None:
        """
        Set the trigger source.

        Args:
            source: Channel number (1-4) or source name ('EXT', 'LINE', etc.)
        """
        if isinstance(source, int):
            self._validate_channel(source)
            source = self.CHANNELS[source]
        self.write(f":TRIG:EDGE:SOUR {source}")

    def get_trigger_source(self) -> str:
        """
        Get the trigger source.

        Returns:
            Trigger source
        """
        return self.query(":TRIG:EDGE:SOUR?")

    def set_trigger_level(self, level: float, source: Optional[Union[int, str]] = None) -> None:
        """
        Set the trigger level.

        Args:
            level: Trigger level in volts
            source: Channel number or source name (if None, uses current source)
        """
        if source is None:
            self.write(f":TRIG:LEV {level}")
        else:
            if isinstance(source, int):
                self._validate_channel(source)
                source = self.CHANNELS[source]
            self.write(f":TRIG:LEV {source},{level}")

    def get_trigger_level(self, source: Optional[Union[int, str]] = None) -> float:
        """
        Get the trigger level.

        Args:
            source: Channel number or source name (if None, uses current source)

        Returns:
            Trigger level in volts
        """
        if source is None:
            return float(self.query(":TRIG:LEV?"))
        else:
            if isinstance(source, int):
                self._validate_channel(source)
                source = self.CHANNELS[source]
            return float(self.query(f":TRIG:LEV? {source}"))

    def set_trigger_slope(self, slope: str) -> None:
        """
        Set the trigger slope/edge.

        Args:
            slope: Trigger slope ('POS', 'NEG', 'EITH', 'ALT')
        """
        slope = slope.upper()
        if slope not in ['POS', 'NEG', 'EITH', 'ALT']:
            raise ValueError("Slope must be 'POS', 'NEG', 'EITH', or 'ALT'")
        self.write(f":TRIG:EDGE:SLOP {slope}")

    def get_trigger_slope(self) -> str:
        """
        Get the trigger slope.

        Returns:
            Trigger slope
        """
        return self.query(":TRIG:EDGE:SLOP?")

    def set_trigger_sweep(self, sweep: str) -> None:
        """
        Set the trigger sweep mode.

        Args:
            sweep: Sweep mode ('AUTO' or 'NORM')
                   AUTO: Auto-triggers if no event occurs within timeout
                   NORM: Waits for a valid trigger event before acquiring
        """
        sweep = sweep.upper()
        if sweep not in ['AUTO', 'NORM']:
            raise ValueError("Sweep must be 'AUTO' or 'NORM'")
        self.write(f":TRIG:SWE {sweep}")

    def get_trigger_sweep(self) -> str:
        """
        Get the trigger sweep mode.

        Returns:
            Trigger sweep mode ('AUTO' or 'NORM')
        """
        return self.query(":TRIG:SWE?")

    def set_trigger_holdoff(self, holdoff: float) -> None:
        """
        Set the trigger holdoff time.

        Args:
            holdoff: Holdoff time in seconds (e.g., 0.02 for 20ms)
        """
        self.write(f":TRIG:HOLD {holdoff}")

    def get_trigger_holdoff(self) -> float:
        """
        Get the trigger holdoff time.

        Returns:
            Holdoff time in seconds
        """
        return float(self.query(":TRIG:HOLD?"))

    # ========== Waveform Acquisition ==========

    def set_waveform_source(self, channel: int) -> None:
        """
        Set the source for waveform queries.

        Args:
            channel: Channel number (1-4)
        """
        self._validate_channel(channel)
        self.write(f":WAV:SOUR {self.CHANNELS[channel]}")

    def set_waveform_format(self, format: str = 'BYTE') -> None:
        """
        Set the waveform data format.

        Args:
            format: Data format ('BYTE', 'WORD', 'ASCII')
        """
        format = format.upper()
        if format not in ['BYTE', 'WORD', 'ASCII']:
            raise ValueError("Format must be 'BYTE', 'WORD', or 'ASCII'")
        self.write(f":WAV:FORM {format}")

    def set_waveform_points_mode(self, mode: str = 'NORM') -> None:
        """
        Set the waveform points mode.

        Args:
            mode: Points mode ('NORM', 'MAX', 'RAW')
        """
        mode = mode.upper()
        if mode not in ['NORM', 'MAX', 'RAW']:
            raise ValueError("Mode must be 'NORM', 'MAX', or 'RAW'")
        self.write(f":WAV:POIN:MODE {mode}")

    def set_waveform_points(self, points: int) -> None:
        """
        Set the number of waveform points to transfer.

        Args:
            points: Number of points
        """
        self.write(f":WAV:POIN {points}")

    def get_waveform_preamble(self) -> dict:
        """
        Get the waveform preamble information.

        Returns:
            Dictionary containing waveform parameters:
                - format: Data format
                - type: Acquisition type
                - points: Number of points
                - count: Average count
                - xincrement: Time between data points
                - xorigin: First data point time
                - xreference: Reference point
                - yincrement: Voltage per LSB
                - yorigin: Voltage at center
                - yreference: Reference point
        """
        preamble_str = self.query(":WAV:PRE?")
        preamble = preamble_str.split(',')

        return {
            'format': int(preamble[0]),
            'type': int(preamble[1]),
            'points': int(preamble[2]),
            'count': int(preamble[3]),
            'xincrement': float(preamble[4]),
            'xorigin': float(preamble[5]),
            'xreference': int(preamble[6]),
            'yincrement': float(preamble[7]),
            'yorigin': float(preamble[8]),
            'yreference': int(preamble[9])
        }

    def get_waveform(self, channel: int, points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Acquire waveform data from a channel.

        Args:
            channel: Channel number (1-4)
            points: Number of points to acquire (default: 1000)

        Returns:
            Tuple of (time_array, voltage_array) as numpy arrays
        """
        self._validate_channel(channel)

        # Configure waveform acquisition
        self.set_waveform_source(channel)
        self.set_waveform_format('BYTE')
        self.set_waveform_points_mode('NORM')
        self.set_waveform_points(points)

        # Get preamble for scaling
        preamble = self.get_waveform_preamble()

        # Get waveform data
        raw_data = self.query_binary_values(":WAV:DATA?", datatype='B', container=np.array)

        # Convert to voltage
        voltage = (raw_data - preamble['yreference']) * preamble['yincrement'] + preamble['yorigin']

        # Create time array
        time = np.arange(preamble['points']) * preamble['xincrement'] + preamble['xorigin']

        return time, voltage

    # ========== Measurements ==========

    def measure_vpp(self, channel: int) -> float:
        """
        Measure peak-to-peak voltage.

        Args:
            channel: Channel number (1-4)

        Returns:
            Peak-to-peak voltage in volts
        """
        self._validate_channel(channel)
        return float(self.query(f":MEAS:VPP? {self.CHANNELS[channel]}"))

    def measure_vmax(self, channel: int) -> float:
        """
        Measure maximum voltage.

        Args:
            channel: Channel number (1-4)

        Returns:
            Maximum voltage in volts
        """
        self._validate_channel(channel)
        return float(self.query(f":MEAS:VMAX? {self.CHANNELS[channel]}"))

    def measure_vmin(self, channel: int) -> float:
        """
        Measure minimum voltage.

        Args:
            channel: Channel number (1-4)

        Returns:
            Minimum voltage in volts
        """
        self._validate_channel(channel)
        return float(self.query(f":MEAS:VMIN? {self.CHANNELS[channel]}"))

    def measure_vavg(self, channel: int) -> float:
        """
        Measure average voltage.

        Args:
            channel: Channel number (1-4)

        Returns:
            Average voltage in volts
        """
        self._validate_channel(channel)
        return float(self.query(f":MEAS:VAV? {self.CHANNELS[channel]}"))

    def measure_vrms(self, channel: int) -> float:
        """
        Measure RMS voltage.

        Args:
            channel: Channel number (1-4)

        Returns:
            RMS voltage in volts
        """
        self._validate_channel(channel)
        return float(self.query(f":MEAS:VRMS? {self.CHANNELS[channel]}"))

    def measure_frequency(self, channel: int) -> float:
        """
        Measure frequency.

        Args:
            channel: Channel number (1-4)

        Returns:
            Frequency in Hz
        """
        self._validate_channel(channel)
        return float(self.query(f":MEAS:FREQ? {self.CHANNELS[channel]}"))

    def measure_period(self, channel: int) -> float:
        """
        Measure period.

        Args:
            channel: Channel number (1-4)

        Returns:
            Period in seconds
        """
        self._validate_channel(channel)
        return float(self.query(f":MEAS:PER? {self.CHANNELS[channel]}"))

    def measure_duty_cycle(self, channel: int) -> float:
        """
        Measure duty cycle.

        Args:
            channel: Channel number (1-4)

        Returns:
            Duty cycle in percent
        """
        self._validate_channel(channel)
        return float(self.query(f":MEAS:DUT? {self.CHANNELS[channel]}"))

    # ========== Utility Methods ==========

    def _validate_channel(self, channel: int) -> None:
        """
        Validate channel number.

        Args:
            channel: Channel number to validate

        Raises:
            ValueError: If channel is not 1-4
        """
        if channel not in self.CHANNELS:
            raise ValueError(f"Invalid channel: {channel}. Must be 1-4.")

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
        return f"DSOX4034A({self.resource_string}, {connected})"
