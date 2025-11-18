"""
Digilent Analog Discovery 2 Control Module

This module provides a Python class for controlling the Digilent Analog Discovery 2
using the WaveForms SDK (DWF library).

The Analog Discovery 2 features:
- 2 Analog Input channels (oscilloscope, 14-bit, 100MS/s)
- 2 Analog Output channels (waveform generator)
- Power supplies (+5V, -5V)
- 16 Digital I/O channels

Requirements:
    - Digilent WaveForms software installed
    - dwf library (comes with WaveForms)

References:
    - WaveForms SDK Reference Manual
    - https://digilent.com/reference/software/waveforms/waveforms-sdk/start
"""

import ctypes
import sys
import time
from typing import Optional, Tuple

# Load the DWF library
if sys.platform == "win32":
    _dwf = ctypes.cdll.dwf
elif sys.platform == "darwin":
    _dwf = ctypes.cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    _dwf = ctypes.cdll.LoadLibrary("libdwf.so")


class AnalogDiscovery2:
    """
    Digilent Analog Discovery 2 Control Class

    This class provides methods to control the Analog Discovery 2 including
    analog input (voltmeter/oscilloscope), analog output, and power supplies.

    Example:
        >>> # Connect to first available device
        >>> ad2 = AnalogDiscovery2()
        >>> ad2.connect()
        >>>
        >>> # Enable 5V power supply
        >>> ad2.set_power_supply(voltage_pos=5.0)
        >>>
        >>> # Read DC voltage from channel 1
        >>> voltage = ad2.read_analog_input(channel=0)
        >>> print(f"Voltage: {voltage} V")
        >>>
        >>> # Disconnect
        >>> ad2.disconnect()
    """

    def __init__(self, device_index: int = -1):
        """
        Initialize the Analog Discovery 2 interface.

        Args:
            device_index: Device index to connect to (-1 for first available)
        """
        self.device_index = device_index
        self.hdwf = ctypes.c_int(0)
        self._connected = False

    def connect(self) -> None:
        """
        Connect to the Analog Discovery 2.

        Raises:
            ConnectionError: If connection fails
        """
        # Open device
        _dwf.FDwfDeviceOpen(ctypes.c_int(self.device_index), ctypes.byref(self.hdwf))

        if self.hdwf.value == 0:
            # Get error message
            szerr = ctypes.create_string_buffer(512)
            _dwf.FDwfGetLastErrorMsg(szerr)
            raise ConnectionError(f"Failed to connect to Analog Discovery 2: {szerr.value.decode()}")

        self._connected = True

        # Get device name
        device_name = ctypes.create_string_buffer(64)
        _dwf.FDwfEnumDeviceName(ctypes.c_int(self.device_index if self.device_index >= 0 else 0), device_name)

        print(f"Connected to: {device_name.value.decode()}")

    def disconnect(self) -> None:
        """Close the connection to the device."""
        if self._connected:
            # Disable power supplies before closing
            _dwf.FDwfAnalogIOEnableSet(self.hdwf, ctypes.c_int(0))
            _dwf.FDwfDeviceClose(self.hdwf)
            self._connected = False
            print("Disconnected from Analog Discovery 2")

    def _check_connected(self) -> None:
        """Check if device is connected."""
        if not self._connected:
            raise RuntimeError("Not connected to device. Call connect() first.")

    # ========== Power Supply Control ==========

    def set_power_supply(self, voltage_pos: float = 5.0, voltage_neg: float = 0.0,
                        enable: bool = True) -> None:
        """
        Configure and enable power supplies.

        Args:
            voltage_pos: Positive supply voltage (0 to 5V)
            voltage_neg: Negative supply voltage (0 to -5V, enter as positive)
            enable: Enable or disable power supplies
        """
        self._check_connected()

        # Enable positive supply
        _dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ctypes.c_int(0), ctypes.c_int(0),
                                        ctypes.c_double(1 if enable else 0))
        # Set positive voltage
        _dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ctypes.c_int(0), ctypes.c_int(1),
                                        ctypes.c_double(voltage_pos))

        # Enable negative supply
        _dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ctypes.c_int(1), ctypes.c_int(0),
                                        ctypes.c_double(1 if enable and voltage_neg > 0 else 0))
        # Set negative voltage
        _dwf.FDwfAnalogIOChannelNodeSet(self.hdwf, ctypes.c_int(1), ctypes.c_int(1),
                                        ctypes.c_double(voltage_neg))

        # Enable master switch
        _dwf.FDwfAnalogIOEnableSet(self.hdwf, ctypes.c_int(1 if enable else 0))

        if enable:
            print(f"Power supply enabled: +{voltage_pos}V" +
                  (f", -{voltage_neg}V" if voltage_neg > 0 else ""))
        else:
            print("Power supply disabled")

    def get_power_supply_status(self) -> Tuple[float, float, float, float]:
        """
        Get power supply status (voltage and current).

        Returns:
            Tuple of (usb_voltage, usb_current, aux_voltage, aux_current)
        """
        self._check_connected()

        # Read USB voltage
        usb_voltage = ctypes.c_double()
        _dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, ctypes.c_int(2), ctypes.c_int(0),
                                          ctypes.byref(usb_voltage))

        # Read USB current
        usb_current = ctypes.c_double()
        _dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, ctypes.c_int(2), ctypes.c_int(1),
                                          ctypes.byref(usb_current))

        return (usb_voltage.value, usb_current.value, 0.0, 0.0)

    # ========== Analog Input (Voltmeter/Oscilloscope) ==========

    def configure_analog_input(self, channel: int = 0, range_v: float = 5.0,
                               offset: float = 0.0) -> None:
        """
        Configure analog input channel for DC voltage measurement.

        Args:
            channel: Input channel (0 or 1)
            range_v: Voltage range in volts (peak-to-peak)
            offset: Voltage offset in volts
        """
        self._check_connected()

        if channel not in [0, 1]:
            raise ValueError("Channel must be 0 or 1")

        # Enable the channel
        _dwf.FDwfAnalogInChannelEnableSet(self.hdwf, ctypes.c_int(channel), ctypes.c_int(1))

        # Set voltage range
        _dwf.FDwfAnalogInChannelRangeSet(self.hdwf, ctypes.c_int(channel),
                                        ctypes.c_double(range_v))

        # Set offset
        _dwf.FDwfAnalogInChannelOffsetSet(self.hdwf, ctypes.c_int(channel),
                                         ctypes.c_double(offset))

        # Set acquisition mode to record (for DC measurements)
        _dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, ctypes.c_int(1))  # acqmodeScanShift

        # Set sample rate
        _dwf.FDwfAnalogInFrequencySet(self.hdwf, ctypes.c_double(100000))  # 100kHz

        # Set buffer size
        _dwf.FDwfAnalogInBufferSizeSet(self.hdwf, ctypes.c_int(1000))

        print(f"Analog input CH{channel+1} configured: Range ±{range_v/2}V, Offset {offset}V")

    def read_analog_input(self, channel: int = 0, samples: int = 100) -> Optional[float]:
        """
        Read DC voltage from analog input channel.

        Takes multiple samples and returns the average for noise reduction.

        Args:
            channel: Input channel (0 or 1)
            samples: Number of samples to average

        Returns:
            Average voltage in volts
        """
        self._check_connected()

        if channel not in [0, 1]:
            raise ValueError("Channel must be 0 or 1")

        # Set to single acquisition mode
        _dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, ctypes.c_int(0))  # acqmodeSingle

        # Set buffer size
        _dwf.FDwfAnalogInBufferSizeSet(self.hdwf, ctypes.c_int(samples))

        # Configure and start acquisition
        _dwf.FDwfAnalogInConfigure(self.hdwf, ctypes.c_int(1), ctypes.c_int(1))

        # Wait for acquisition with timeout
        sts = ctypes.c_byte()
        timeout = 100  # 100 iterations = ~1 second
        for _ in range(timeout):
            _dwf.FDwfAnalogInStatus(self.hdwf, ctypes.c_int(1), ctypes.byref(sts))
            if sts.value == 2:  # DwfStateDone
                break
            time.sleep(0.01)
        else:
            print(f"Warning: Acquisition timeout (status={sts.value})")
            return None

        # Read samples
        rg_samples = (ctypes.c_double * samples)()
        _dwf.FDwfAnalogInStatusData(self.hdwf, ctypes.c_int(channel), rg_samples, ctypes.c_int(samples))

        # Calculate average
        avg = sum(rg_samples) / samples
        return avg

    def read_analog_input_fast(self, channel: int = 0) -> Optional[float]:
        """
        Read single DC voltage sample from analog input (faster, less accurate).

        Args:
            channel: Input channel (0 or 1)

        Returns:
            Voltage in volts
        """
        self._check_connected()

        if channel not in [0, 1]:
            raise ValueError("Channel must be 0 or 1")

        # Get current sample value
        sample = ctypes.c_double()
        _dwf.FDwfAnalogInStatusSample(self.hdwf, ctypes.c_int(channel), ctypes.byref(sample))

        return sample.value

    def start_continuous_acquisition(self, channel: int = 0) -> None:
        """
        Start continuous acquisition mode for fast repeated readings.

        Args:
            channel: Input channel (0 or 1)
        """
        self._check_connected()

        # Set to scan shift mode for continuous acquisition
        _dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, ctypes.c_int(1))  # acqmodeScanShift

        # Start acquisition
        _dwf.FDwfAnalogInConfigure(self.hdwf, ctypes.c_int(0), ctypes.c_int(1))

        print(f"Started continuous acquisition on CH{channel+1}")

    # ========== Analog Output (Waveform Generator) ==========

    def set_analog_output_dc(self, channel: int = 0, voltage: float = 0.0) -> None:
        """
        Set analog output to DC voltage.

        Args:
            channel: Output channel (0 or 1)
            voltage: DC voltage in volts (-5V to +5V)
        """
        self._check_connected()

        if channel not in [0, 1]:
            raise ValueError("Channel must be 0 or 1")

        # Enable channel
        _dwf.FDwfAnalogOutNodeEnableSet(self.hdwf, ctypes.c_int(channel), ctypes.c_int(0),
                                        ctypes.c_int(1))

        # Set to DC function
        _dwf.FDwfAnalogOutNodeFunctionSet(self.hdwf, ctypes.c_int(channel), ctypes.c_int(0),
                                          ctypes.c_int(0))  # funcDC

        # Set offset (DC level)
        _dwf.FDwfAnalogOutNodeOffsetSet(self.hdwf, ctypes.c_int(channel), ctypes.c_int(0),
                                        ctypes.c_double(voltage))

        # Configure and start
        _dwf.FDwfAnalogOutConfigure(self.hdwf, ctypes.c_int(channel), ctypes.c_int(1))

        print(f"Analog output CH{channel+1} set to {voltage}V DC")

    # ========== Utility Methods ==========

    def reset(self) -> None:
        """Reset the device to default configuration."""
        self._check_connected()
        _dwf.FDwfDeviceReset(self.hdwf)
        print("Device reset to defaults")

    def get_temperature(self) -> float:
        """
        Get device internal temperature.

        Returns:
            Temperature in Celsius
        """
        self._check_connected()
        temp = ctypes.c_double()
        _dwf.FDwfAnalogIOChannelNodeStatus(self.hdwf, ctypes.c_int(2), ctypes.c_int(2),
                                          ctypes.byref(temp))
        return temp.value

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __repr__(self) -> str:
        """String representation."""
        connected = "connected" if self._connected else "disconnected"
        return f"AnalogDiscovery2({connected})"
