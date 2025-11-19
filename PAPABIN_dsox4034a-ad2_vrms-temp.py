"""
Dual Instrument Logger - Analog Discovery 2 + DSOX4034A

This script reads from both instruments simultaneously:
- Digilent Analog Discovery 2: DC Voltage from NTC voltage divider (also provides 5V excitation)
- Keysight DSOX4034A: Channel 1 Vrms

Also calculates NTC temperature using Beta equation (R25=7K, B=3600K).
Records Elapsed Time in ms and hr for plotting with GENERAL_all_plot-results.py.

NTC Circuit:
    AD2 V+ (5V) ---- [NTC] ---- [6.8k Ref] ---- GND
                           |
                       AD2 CH1+ (to AD2 analog input)

Settings:
- Measurement interval: 300ms
- Oscilloscope timebase: 5ms/div
- Trigger holdoff: 5ms
- Save interval: 20 measurements

Default Resources:
- AD2: First available device
- Scope: TCPIP::192.168.2.60::INSTR

Requirements:
- Digilent WaveForms software installed

Usage:
    python PAPABIN_dsox4034a-ad2_vrms-temp.py

Press Ctrl+C to stop logging.
"""

import sys
import signal
import time
import math

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])

from instruments.base_logger import BaseDataLogger
from instruments.digilent import AnalogDiscovery2
from instruments.keysight import DSOX4034A


class DualInstrumentLoggerAD2(BaseDataLogger):
    """
    Dual instrument logger using Analog Discovery 2 and DSOX4034A.

    AD2 provides:
    - 5V DC excitation for NTC circuit
    - DC voltage measurement for temperature calculation

    DSOX4034A provides:
    - Channel 1 Vrms measurement

    NTC Parameters:
        R25 = 7K ohm
        B25/85 = 3600K
        Reference resistor = 6.8K ohm
    """

    # NTC thermistor parameters
    V_EXCITATION = 5.0      # Excitation voltage (V) from AD2 power supply
    R_REFERENCE = 6800.0    # Reference resistor (ohms) - 6.8K for best sensitivity at 25°C

    # NTC Beta parameters
    # R25 = 7K ohm (resistance at 25°C)
    # B25/85 = 3600K (Beta value)
    R25 = 7000.0            # Resistance at 25°C (ohms)
    BETA = 3600.0           # Beta value (K)
    T25 = 298.15            # 25°C in Kelvin

    def __init__(self, ad2_device_index=-1, scope_resource=None, **kwargs):
        """
        Initialize the dual instrument logger.

        Args:
            ad2_device_index: AD2 device index (-1 for first available)
            scope_resource: VISA resource string for DSOX4034A (None for default)
            **kwargs: Additional arguments for BaseDataLogger
        """
        # Settings: 300ms interval, save every 20 measurements
        kwargs.setdefault('measurement_interval', 0.3)  # 300ms
        kwargs.setdefault('save_interval', 20)
        super().__init__(**kwargs)

        self.ad2_device_index = ad2_device_index
        self.scope_resource = scope_resource
        self.ad2 = None
        self.scope = None

    def calculate_ntc_resistance(self, voltage):
        """
        Calculate NTC resistance from voltage divider measurement.

        Circuit: 5V -- [NTC] -- [6.8k] -- GND
                            |
                        V_measured

        Args:
            voltage: Measured voltage at divider midpoint

        Returns:
            NTC resistance in ohms
        """
        if voltage <= 0 or voltage >= self.V_EXCITATION:
            return None

        # R_NTC = R_ref * (V_exc - V_meas) / V_meas
        r_ntc = self.R_REFERENCE * (self.V_EXCITATION - voltage) / voltage
        return r_ntc

    def calculate_temperature(self, resistance):
        """
        Calculate temperature from NTC resistance using Beta equation.

        T = 1 / (1/T25 + (1/B) * ln(R/R25))

        This is derived from: R(T) = R25 * exp(B * (1/T - 1/T25))

        Args:
            resistance: NTC resistance in ohms

        Returns:
            Temperature in Celsius
        """
        if resistance is None or resistance <= 0:
            return None

        try:
            # Beta equation: 1/T = 1/T25 + (1/B) * ln(R/R25)
            inv_t = (1.0 / self.T25) + (1.0 / self.BETA) * math.log(resistance / self.R25)
            temp_k = 1.0 / inv_t
            temp_c = temp_k - 273.15
            return temp_c
        except (ValueError, ZeroDivisionError):
            return None

    def setup_instrument(self):
        """Connect and configure both instruments."""
        # ===== Setup Analog Discovery 2 =====
        print("="*50)
        print("Setting up Digilent Analog Discovery 2...")
        print("="*50)
        self.ad2 = AnalogDiscovery2(self.ad2_device_index)
        self.ad2.connect()

        # Enable 5V power supply for NTC excitation
        print("Enabling 5V power supply for NTC excitation...")
        self.ad2.set_power_supply(voltage_pos=5.0, enable=True)

        # Wait for power supply to stabilize
        time.sleep(0.5)

        # Configure analog input for DC voltage measurement
        print("Configuring analog input CH1...")
        self.ad2.configure_analog_input(channel=0, range_v=10.0, offset=0.0)

        # ===== Setup DSOX4034A Oscilloscope =====
        print("\n" + "="*50)
        print("Setting up Keysight DSOX4034A Oscilloscope...")
        print("="*50)
        self.scope = DSOX4034A(self.scope_resource)
        self.scope.connect()

        # Ensure Channel 1 is on
        self.scope.channel_on(1)

        # Set timebase to 5ms/div
        timebase_scale = 0.005  # 5ms = 0.005s
        print(f"Setting timebase to 5 ms/div...")
        self.scope.set_timebase_scale(timebase_scale)
        current_timebase = self.scope.get_timebase_scale()
        print(f"  Timebase confirmed: {current_timebase*1000:.1f} ms/div")

        # Set oscilloscope to RUN mode
        self.scope.run()

        # Configure trigger for consistent measurement speed
        print("Configuring trigger...")
        self.scope.set_trigger_sweep("AUTO")
        self.scope.set_trigger_level(0.0, 1)
        self.scope.set_trigger_holdoff(0.005)  # 5ms holdoff
        print("  Trigger sweep: AUTO")
        print("  Trigger level: 0.0 V")
        print("  Trigger holdoff: 5 ms")

        # Set up VRMS measurement on scope
        print("Configuring scope measurements...")
        self.scope.write(":MEAS:CLE")
        self.scope.write(":MEAS:VRMS CHAN1")
        self.scope.write(":MEAS:STAT OFF")

        # Wait for measurement to stabilize
        time.sleep(0.5)

        # Test measurements
        print("\nTesting measurements...")
        try:
            test_voltage = self.ad2.read_analog_input(channel=0, samples=100)
            print(f"  AD2 DC Voltage: {test_voltage:.6f} V")

            # Calculate and display NTC values
            r_ntc = self.calculate_ntc_resistance(test_voltage)
            if r_ntc:
                temp_c = self.calculate_temperature(r_ntc)
                print(f"  NTC Resistance: {r_ntc:.1f} ohms")
                if temp_c:
                    print(f"  NTC Temperature: {temp_c:.2f} C")
        except Exception as e:
            print(f"  AD2 test failed: {e}")

        try:
            test_vrms = float(self.scope.query(":MEAS:VRMS? CHAN1"))
            print(f"  Scope Vrms: {test_vrms:.6f} V")
        except Exception as e:
            print(f"  Scope test failed: {e}")

        print("\n" + "="*50)
        print("Both instruments configured successfully!")
        print("="*50)

    def read_measurement(self):
        """
        Read measurements from both instruments and calculate temperature.

        Returns:
            Tuple of (dc_voltage, vrms, temperature) or None if error
        """
        dc_voltage = None
        vrms = None
        temperature = None

        # Read DC voltage from AD2 (use averaging for accuracy)
        try:
            dc_voltage = self.ad2.read_analog_input(channel=0, samples=50)

            # Calculate NTC temperature from voltage
            if dc_voltage is not None:
                r_ntc = self.calculate_ntc_resistance(dc_voltage)
                temperature = self.calculate_temperature(r_ntc)
        except Exception as e:
            print(f"Error reading AD2: {e}")

        # Read Vrms from oscilloscope
        try:
            vrms_str = self.scope.query(":MEAS:VRMS? CHAN1")
            vrms = float(vrms_str)
        except Exception as e:
            print(f"Error reading scope: {e}")

        # Return None if both failed
        if dc_voltage is None and vrms is None:
            return None

        # Return tuple (use 0.0 for failed readings, None for temperature if calculation failed)
        return (dc_voltage or 0.0, vrms or 0.0, temperature)

    def cleanup_instrument(self):
        """Disconnect both instruments."""
        if self.ad2:
            self.ad2.disconnect()
        if self.scope:
            self.scope.disconnect()

    def get_headers(self):
        """Return Excel column headers."""
        return ["Timestamp", "DC Voltage (V)", "Vrms CH1 (V)", "Temperature (C)", "Elapsed Time (ms)", "Elapsed Time (hr)"]

    def format_measurement(self, timestamp_str, elapsed_ms, measurement):
        """Format measurement tuple into Excel row."""
        dc_voltage, vrms, temperature = measurement
        elapsed_hr = elapsed_ms / 3_600_000  # Convert ms to hours
        return [timestamp_str, dc_voltage, vrms, temperature, elapsed_ms, elapsed_hr]

    def format_display(self, timestamp_str, elapsed_ms, measurement):
        """Format measurements for console display."""
        if measurement is not None:
            dc_voltage, vrms, temperature = measurement
            temp_str = f"{temperature:7.2f}" if temperature is not None else "   N/A"
            return f"{timestamp_str} | DC: {dc_voltage:8.4f} V | Vrms: {vrms:8.4f} V | Temp: {temp_str} C | {elapsed_ms:8.1f} ms"
        return f"{timestamp_str} | Error | {elapsed_ms:8.1f} ms"


def signal_handler(signum, frame):
    """Handle Ctrl+C signal."""
    print("\n\nReceived interrupt signal. Stopping...")
    sys.exit(0)


def main():
    """Main entry point."""
    print("="*60)
    print("Dual Instrument Logger (AD2 + DSOX4034A)")
    print("="*60)
    print(f"AD2: First available device")
    print(f"Scope: {DSOX4034A.DEFAULT_RESOURCE}")
    print("="*60)

    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start logger
    logger = DualInstrumentLoggerAD2()
    logger.start()


if __name__ == "__main__":
    main()
