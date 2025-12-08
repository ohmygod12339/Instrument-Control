"""
Anbai AT4516 Multi-channel Temperature Meter Control Module

This module provides a Python class for controlling the Anbai AT4516
(AT45xx series) Multi-channel Temperature Meter via RS-232 serial communication.

The AT4516 is an 8-channel temperature meter with:
- Support for various thermocouple types (K, T, J, N, E, S, R, B)
- Temperature range: -200°C to 1800°C (varies by thermocouple type)
- Resolution: 0.1°C
- Expandable to 128 channels via RS-485
- SCPI command protocol

References:
    - AT45xx Multi-channel Temperature Meter User's Guide Rev.B5
    - Applent Instruments Inc.
"""

import serial
import serial.tools.list_ports
from typing import Optional, List, Dict, Union
import time


class AT4516:
    """
    Anbai AT4516 Multi-channel Temperature Meter Control Class

    This class provides methods to control and acquire temperature measurements
    from an Anbai AT4516 temperature meter using SCPI commands over RS-232.

    Attributes:
        port (str): Serial COM port (e.g., 'COM3')
        baudrate (int): Serial baud rate
        serial_conn: PySerial connection object
        timeout (float): Command timeout in seconds

    Example:
        >>> # Connect using default COM port
        >>> temp_meter = AT4516()
        >>> temp_meter.connect()
        >>>
        >>> # Or connect with custom COM port
        >>> temp_meter = AT4516(port='COM5', baudrate=115200)
        >>> temp_meter.connect()
        >>> print(temp_meter.identify())
        >>>
        >>> # Set thermocouple type to K-type
        >>> temp_meter.set_thermocouple_type('TC-K')
        >>>
        >>> # Read all channel temperatures
        >>> temperatures = temp_meter.read_all_channels()
        >>> print(f"Temperatures: {temperatures}")
        >>>
        >>> # Read specific channel
        >>> temp = temp_meter.read_channel(1)
        >>> print(f"Channel 1: {temp}°C")
        >>>
        >>> # Disconnect
        >>> temp_meter.disconnect()
    """

    # Default COM port for lab instrument (adjust as needed)
    DEFAULT_PORT = "COM10"
    DEFAULT_BAUDRATE = 9600

    # Supported thermocouple types
    THERMOCOUPLE_TYPES = ['TC-T', 'TC-K', 'TC-J', 'TC-N', 'TC-E', 'TC-S', 'TC-R', 'TC-B']

    # Sampling rates
    RATES = ['SLOW', 'MED', 'FAST']

    # Temperature units
    UNITS = {
        'CEL': '°C',  # Celsius
        'KEL': 'K',   # Kelvin
        'FAH': '°F'   # Fahrenheit
    }

    def __init__(self, port: Optional[str] = None, baudrate: int = DEFAULT_BAUDRATE,
                 timeout: float = 2.0, inter_command_delay: float = 0.15):
        """
        Initialize the AT4516 temperature meter interface.

        Args:
            port: Serial COM port (default: DEFAULT_PORT)
                Format: "COM3", "COM4", etc. on Windows
                        "/dev/ttyUSB0" on Linux
                If None, uses the lab's default instrument
            baudrate: Serial baud rate (default: 9600)
                Options: 9600, 19200, 38400, 57600, 115200
            timeout: Command timeout in seconds (default: 2.0)
            inter_command_delay: Delay between commands in seconds (default: 0.15)
                AT4516 needs time to process commands, especially at 9600 baud
        """
        self.port = port or self.DEFAULT_PORT
        self.baudrate = baudrate
        self.timeout = timeout
        self.inter_command_delay = inter_command_delay
        self.serial_conn = None

    def connect(self) -> None:
        """
        Establish connection to the temperature meter.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )

            # Clear input/output buffers
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()

            # Wait for connection to stabilize
            time.sleep(0.3)

            # Verify connection
            idn = self.identify()
            print(f"Connected to: {idn}")

            # Stop any ongoing measurement to ensure clean state
            try:
                self.stop_measurement()
            except:
                pass  # Ignore if already stopped

            # Additional delay for instrument to stabilize
            time.sleep(0.2)

        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")
        except Exception as e:
            raise ConnectionError(f"Unexpected error during connection: {e}")

    def disconnect(self) -> None:
        """Close the connection to the temperature meter."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.serial_conn = None
            print(f"Disconnected from {self.port}")

    def write(self, command: str) -> None:
        """
        Send a SCPI command to the instrument.

        Args:
            command: SCPI command string (terminator will be added automatically)

        Raises:
            RuntimeError: If not connected
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            raise RuntimeError("Not connected to instrument")

        # Add line feed terminator if not present
        if not command.endswith('\n'):
            command += '\n'

        self.serial_conn.write(command.encode('ascii'))
        self.serial_conn.flush()

        # Wait after sending command (instrument needs processing time)
        time.sleep(self.inter_command_delay)

    def query(self, command: str) -> str:
        """
        Send a SCPI query command and read the response.

        Args:
            command: SCPI query command string (should end with '?')

        Returns:
            Response string from the instrument

        Raises:
            RuntimeError: If not connected
            TimeoutError: If no response received
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            raise RuntimeError("Not connected to instrument")

        # Clear input buffer before query
        self.serial_conn.reset_input_buffer()

        # Send query
        if not command.endswith('\n'):
            command += '\n'

        self.serial_conn.write(command.encode('ascii'))
        self.serial_conn.flush()

        # Wait for instrument to process query (critical for AT4516)
        time.sleep(self.inter_command_delay)

        # Read response (terminated by \n)
        try:
            response = self.serial_conn.readline().decode('ascii').strip()
            if not response:
                raise TimeoutError(f"No response received for query: {command}")

            # Additional delay after receiving response
            time.sleep(self.inter_command_delay)

            return response
        except serial.SerialTimeoutException:
            raise TimeoutError(f"Timeout waiting for response to: {command}")

    def identify(self) -> str:
        """
        Query the instrument identification string.

        Returns:
            Identification string containing model, revision, serial number, manufacturer

        Example:
            >>> temp_meter.identify()
            'AT4532,Rev.B5,SN123456,Applent Instruments'
        """
        return self.query("*IDN?")

    def check_error(self) -> str:
        """
        Query the last error from the instrument.

        Returns:
            Error string ("no error" if no errors)
        """
        return self.query("ERROR?")

    # =====================================================================
    # Measurement Control (MEAS Subsystem)
    # =====================================================================

    def set_thermocouple_type(self, tc_type: str) -> None:
        """
        Set the thermocouple type for all channels.

        Args:
            tc_type: Thermocouple type string
                Options: 'TC-T', 'TC-K', 'TC-J', 'TC-N', 'TC-E', 'TC-S', 'TC-R', 'TC-B'

        Example:
            >>> temp_meter.set_thermocouple_type('TC-K')  # K-type thermocouple
        """
        tc_type = tc_type.upper()
        if tc_type not in self.THERMOCOUPLE_TYPES:
            raise ValueError(f"Invalid thermocouple type. Must be one of {self.THERMOCOUPLE_TYPES}")

        self.write(f"MEAS:MODEL {tc_type}")

    def get_thermocouple_type(self) -> str:
        """
        Query the current thermocouple type.

        Returns:
            Current thermocouple type (e.g., 'tc-k')
        """
        return self.query("MEAS:MODEL?")

    def set_channel_thermocouple(self, channel: int, tc_type: str) -> None:
        """
        Set the thermocouple type for a specific channel.

        Args:
            channel: Channel number (1-8)
            tc_type: Thermocouple type string

        Example:
            >>> temp_meter.set_channel_thermocouple(1, 'TC-K')
        """
        if not 1 <= channel <= 8:
            raise ValueError("Channel must be between 1 and 8")

        tc_type = tc_type.upper()
        if tc_type not in self.THERMOCOUPLE_TYPES:
            raise ValueError(f"Invalid thermocouple type. Must be one of {self.THERMOCOUPLE_TYPES}")

        self.write(f"MEAS:CMODEL <{channel:03d}>,<{tc_type}>")

    def set_sampling_rate(self, rate: str) -> None:
        """
        Set the sampling rate (measurement speed).

        Args:
            rate: Sampling rate string
                Options: 'SLOW', 'MED', 'FAST'
                - SLOW: 1s per sample
                - MED: 0.5s per sample
                - FAST: 0.1s per sample (increases with more channels)

        Example:
            >>> temp_meter.set_sampling_rate('FAST')
        """
        rate = rate.upper()
        if rate not in self.RATES:
            raise ValueError(f"Invalid rate. Must be one of {self.RATES}")

        self.write(f"MEAS:RATE {rate}")

    def get_sampling_rate(self) -> str:
        """
        Query the current sampling rate.

        Returns:
            Current sampling rate ('fast', 'med', or 'slow')
        """
        return self.query("MEAS:RATE?")

    def start_measurement(self, wait_for_reading: bool = True) -> None:
        """
        Start the measurement/sampling.

        Args:
            wait_for_reading: If True, waits for first measurement cycle to complete
                            and performs a dummy read to ensure valid data.
                            This is CRITICAL after power-on or configuration changes.
        """
        self.write("MEAS:START ON")

        if wait_for_reading:
            # Get current sampling rate to determine wait time
            try:
                rate = self.get_sampling_rate().lower()
            except:
                rate = 'slow'  # Default to slowest (safest)

            # Wait times based on manual specs (page 16-17)
            # SLOW: 1s, MED: 0.5s, FAST: 0.1s (but increases with channels, up to 0.5s for 8ch)
            wait_times = {
                'slow': 1.5,   # 1s + margin
                'med': 1.0,    # 0.5s + margin
                'fast': 1.0,   # 0.5s (for 8 channels) + margin
            }
            wait_time = wait_times.get(rate, 1.5)

            print(f"   Waiting {wait_time}s for first measurement cycle...")
            time.sleep(wait_time)

            # Perform dummy read to flush buffers and ensure readings are valid
            try:
                _ = self.read_all_channels()
                print("   Dummy read complete - instrument ready")
            except:
                pass  # Ignore errors on dummy read

    def stop_measurement(self) -> None:
        """Stop the measurement/sampling."""
        self.write("MEAS:START OFF")
        time.sleep(0.3)  # Wait for stop to complete

    def enable_channel(self, channel: int) -> None:
        """
        Enable a specific channel.

        Args:
            channel: Channel number (1-8)
        """
        if not 1 <= channel <= 8:
            raise ValueError("Channel must be between 1 and 8")

        self.write(f"MEAS:CHANON <{channel:03d}>,<ON>")

    def disable_channel(self, channel: int) -> None:
        """
        Disable a specific channel.

        Args:
            channel: Channel number (1-8)
        """
        if not 1 <= channel <= 8:
            raise ValueError("Channel must be between 1 and 8")

        self.write(f"MEAS:CHANON <{channel:03d}>,<OFF>")

    def read_all_channels(self) -> List[float]:
        """
        Read temperature from all channels.

        Returns:
            List of temperature values (in current unit) for all channels
            Returns None for disabled or error channels

        Example:
            >>> temps = temp_meter.read_all_channels()
            >>> print(temps)
            [23.4, 23.5, 23.3, None, None, None, None, None]
        """
        response = self.query("FETCH?")

        # Parse response: "+2.34000e+01, +2.35000e+01, +2.33000e+01, ..."
        values = []
        for value_str in response.split(','):
            value_str = value_str.strip()
            try:
                values.append(float(value_str))
            except ValueError:
                values.append(None)  # Invalid or disabled channel

        return values

    def read_channel(self, channel: int) -> Optional[float]:
        """
        Read temperature from a specific channel.

        Args:
            channel: Channel number (1-8)

        Returns:
            Temperature value (in current unit) or None if channel is disabled/error

        Example:
            >>> temp = temp_meter.read_channel(1)
            >>> print(f"Channel 1: {temp}°C")
        """
        if not 1 <= channel <= 8:
            raise ValueError("Channel must be between 1 and 8")

        temps = self.read_all_channels()
        return temps[channel - 1] if channel <= len(temps) else None

    # =====================================================================
    # System Settings (SYST Subsystem)
    # =====================================================================

    def enable_comparator(self) -> None:
        """Enable the comparator (limit checking) function."""
        self.write("SYST:COMP ON")

    def disable_comparator(self) -> None:
        """Disable the comparator (limit checking) function."""
        self.write("SYST:COMP OFF")

    def get_comparator_status(self) -> bool:
        """
        Query comparator status.

        Returns:
            True if comparator is ON, False if OFF
        """
        response = self.query("SYST:COMP?").lower()
        return response == 'on'

    def enable_beep(self) -> None:
        """Enable the beep sound."""
        self.write("SYST:BEEP ON")

    def disable_beep(self) -> None:
        """Disable the beep sound."""
        self.write("SYST:BEEP OFF")

    def get_beep_status(self) -> bool:
        """
        Query beep status.

        Returns:
            True if beep is ON, False if OFF
        """
        response = self.query("SYST:BEEP?").lower()
        return response == 'on'

    def set_temperature_unit(self, unit: str) -> None:
        """
        Set the temperature unit.

        Args:
            unit: Temperature unit string
                Options: 'CEL' (Celsius), 'KEL' (Kelvin), 'FAH' (Fahrenheit)

        Example:
            >>> temp_meter.set_temperature_unit('CEL')  # Celsius
        """
        unit = unit.upper()
        if unit not in self.UNITS:
            raise ValueError(f"Invalid unit. Must be one of {list(self.UNITS.keys())}")

        self.write(f"SYST:UNIT {unit}")

    def get_temperature_unit(self) -> str:
        """
        Query the current temperature unit.

        Returns:
            Current temperature unit symbol (e.g., '℃', 'K', 'F')
        """
        return self.query("SYST:UNIT?")

    def set_keypad_lock(self, enable: bool) -> None:
        """
        Enable or disable the keypad lock.

        Args:
            enable: True to lock keypad, False to unlock
        """
        state = "ON" if enable else "OFF"
        self.write(f"MEAS:KEYLOCK {state}")

    def get_keypad_lock_status(self) -> bool:
        """
        Query keypad lock status.

        Returns:
            True if keypad is locked, False if unlocked
        """
        response = self.query("MEAS:KEYLOCK?").lower()
        return response == 'on'

    # =====================================================================
    # Limit Settings
    # =====================================================================

    def set_low_limit(self, limit: float) -> None:
        """
        Set the low limit for all channels (used with comparator).

        Args:
            limit: Low limit temperature value
        """
        self.write(f"MEAS:LOW {limit}")

    def set_high_limit(self, limit: float) -> None:
        """
        Set the high limit for all channels (used with comparator).

        Args:
            limit: High limit temperature value
        """
        self.write(f"MEAS:HIGH {limit}")

    def set_channel_low_limit(self, channel: int, limit: float) -> None:
        """
        Set the low limit for a specific channel.

        Args:
            channel: Channel number (1-8)
            limit: Low limit temperature value
        """
        if not 1 <= channel <= 8:
            raise ValueError("Channel must be between 1 and 8")

        self.write(f"MEAS:CLOW <{channel:03d}>,<{limit}>")

    def set_channel_high_limit(self, channel: int, limit: float) -> None:
        """
        Set the high limit for a specific channel.

        Args:
            channel: Channel number (1-8)
            limit: High limit temperature value
        """
        if not 1 <= channel <= 8:
            raise ValueError("Channel must be between 1 and 8")

        self.write(f"MEAS:CHIGH <{channel:03d}>,<{limit}>")

    def configure_and_start(self, tc_type: str = 'TC-K', rate: str = 'FAST',
                           unit: str = 'CEL') -> None:
        """
        Complete configuration sequence for the AT4516.

        This method performs the correct sequence to configure the instrument:
        1. STOP measurement
        2. Configure thermocouple type (all channels)
        3. Configure sampling rate
        4. Configure temperature unit
        5. START measurement with dummy read

        IMPORTANT: This method is REQUIRED after power-on or any configuration changes
        to ensure valid temperature readings.

        Args:
            tc_type: Thermocouple type (default: 'TC-K')
                Options: 'TC-T', 'TC-K', 'TC-J', 'TC-N', 'TC-E', 'TC-S', 'TC-R', 'TC-B'
            rate: Sampling rate (default: 'FAST')
                Options: 'SLOW' (1s), 'MED' (0.5s), 'FAST' (0.1-0.5s)
            unit: Temperature unit (default: 'CEL')
                Options: 'CEL' (Celsius), 'KEL' (Kelvin), 'FAH' (Fahrenheit)

        Example:
            >>> temp_meter = AT4516()
            >>> temp_meter.connect()
            >>> temp_meter.configure_and_start(tc_type='TC-K', rate='FAST', unit='CEL')
            >>> temps = temp_meter.read_all_channels()
        """
        print(f"\nConfiguring AT4516...")
        print(f"  TC Type: {tc_type}, Rate: {rate}, Unit: {unit}")

        # Step 1: Stop measurement
        print("  1. Stopping measurement...")
        self.stop_measurement()

        # Step 2: Set thermocouple type for all channels
        print(f"  2. Setting thermocouple type to {tc_type}...")
        self.set_thermocouple_type(tc_type)
        time.sleep(0.3)

        # Also set each channel individually (ensures all channels configured)
        for ch in range(1, 9):
            self.set_channel_thermocouple(ch, tc_type)
            time.sleep(0.15)

        # Step 3: Set sampling rate
        print(f"  3. Setting sampling rate to {rate}...")
        self.set_sampling_rate(rate)
        time.sleep(0.2)

        # Step 4: Set temperature unit
        print(f"  4. Setting temperature unit to {unit}...")
        self.set_temperature_unit(unit)
        time.sleep(0.2)

        # Step 5: Start measurement with wait and dummy read
        print("  5. Starting measurement...")
        self.start_measurement(wait_for_reading=True)

        print("✓ Configuration complete - instrument ready!")

    # =====================================================================
    # Utility Methods
    # =====================================================================

    @staticmethod
    def list_available_ports() -> List[str]:
        """
        List all available COM ports on the system.

        Returns:
            List of available COM port names

        Example:
            >>> ports = AT4516.list_available_ports()
            >>> print(f"Available ports: {ports}")
            ['COM3', 'COM4', 'COM5']
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.disconnect()
        return False

    def __repr__(self) -> str:
        """String representation of the instrument."""
        status = "connected" if (self.serial_conn and self.serial_conn.is_open) else "disconnected"
        return f"AT4516(port='{self.port}', baudrate={self.baudrate}, status='{status}')"
