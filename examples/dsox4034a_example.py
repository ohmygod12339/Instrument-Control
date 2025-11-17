"""
Example script for using the DSOX4034A oscilloscope class

This script demonstrates basic operations:
1. Connecting to the oscilloscope
2. Configuring channels and timebase
3. Acquiring waveform data
4. Making measurements
5. Plotting results (optional)
"""

import sys
import os

# Add parent directory to path to import instruments package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from instruments.keysight import DSOX4034A
import numpy as np

# Uncomment to enable plotting
# import matplotlib.pyplot as plt


def basic_connection_example():
    """Basic connection and identification example."""
    print("=" * 60)
    print("Basic Connection Example")
    print("=" * 60)

    # Change this to your oscilloscope's address
    # USB: "USB0::0x0957::0x17A6::MY########::INSTR"
    # Ethernet: "TCPIP0::192.168.1.100::INSTR"
    resource_string = "TCPIP0::192.168.1.100::INSTR"

    # Create oscilloscope object
    scope = DSOX4034A(resource_string)

    try:
        # Connect
        scope.connect()

        # Get identification
        idn = scope.identify()
        print(f"Connected to: {idn}")

        # Check for errors
        error = scope.get_error()
        print(f"Error queue: {error}")

    finally:
        # Always disconnect
        scope.disconnect()


def context_manager_example():
    """Example using context manager (recommended)."""
    print("\n" + "=" * 60)
    print("Context Manager Example")
    print("=" * 60)

    resource_string = "TCPIP0::192.168.1.100::INSTR"

    # Using context manager - automatically connects and disconnects
    with DSOX4034A(resource_string) as scope:
        print(f"Connected to: {scope.identify()}")

        # Autoscale
        print("Performing autoscale...")
        scope.autoscale()

        # Get timebase settings
        time_scale = scope.get_timebase_scale()
        print(f"Timebase scale: {time_scale} s/div")


def channel_configuration_example():
    """Example of channel configuration."""
    print("\n" + "=" * 60)
    print("Channel Configuration Example")
    print("=" * 60)

    resource_string = "TCPIP::192.168.2.60::INSTR"

    with DSOX4034A(resource_string) as scope:
        # Turn on channel 1
        scope.channel_on(1)
        print("Channel 1 enabled")

        # Set channel 1 parameters
        scope.set_channel_scale(1, 0.5)  # 500 mV/div
        scope.set_channel_offset(1, 0.0)  # 0V offset
        scope.set_channel_coupling(1, 'DC')

        print(f"Channel 1 scale: {scope.get_channel_scale(1)} V/div")
        print(f"Channel 1 offset: {scope.get_channel_offset(1)} V")
        print(f"Channel 1 coupling: {scope.get_channel_coupling(1)}")

        # Configure timebase
        scope.set_timebase_scale(100e-6)  # 100 µs/div
        scope.set_timebase_position(0)  # Center

        print(f"Timebase scale: {scope.get_timebase_scale()} s/div")


def trigger_configuration_example():
    """Example of trigger configuration."""
    print("\n" + "=" * 60)
    print("Trigger Configuration Example")
    print("=" * 60)

    resource_string = "TCPIP0::192.168.1.100::INSTR"

    with DSOX4034A(resource_string) as scope:
        # Configure edge trigger
        scope.set_trigger_mode('EDGE')
        scope.set_trigger_source(1)  # Channel 1
        scope.set_trigger_level(0.5)  # 500 mV
        scope.set_trigger_slope('POS')  # Positive edge

        print(f"Trigger mode: {scope.get_trigger_mode()}")
        print(f"Trigger source: {scope.get_trigger_source()}")
        print(f"Trigger level: {scope.get_trigger_level()} V")
        print(f"Trigger slope: {scope.get_trigger_slope()}")


def waveform_acquisition_example():
    """Example of waveform data acquisition."""
    print("\n" + "=" * 60)
    print("Waveform Acquisition Example")
    print("=" * 60)

    resource_string = "TCPIP0::192.168.1.100::INSTR"

    with DSOX4034A(resource_string) as scope:
        # Enable channel 1
        scope.channel_on(1)

        # Configure for a typical measurement
        scope.set_timebase_scale(1e-3)  # 1 ms/div
        scope.set_channel_scale(1, 1.0)  # 1 V/div

        # Perform single acquisition
        print("Acquiring waveform...")
        scope.single()

        # Get waveform data (1000 points)
        time, voltage = scope.get_waveform(channel=1, points=1000)

        print(f"Acquired {len(voltage)} points")
        print(f"Time range: {time[0]:.6e} to {time[-1]:.6e} s")
        print(f"Voltage range: {np.min(voltage):.3f} to {np.max(voltage):.3f} V")
        print(f"Average voltage: {np.mean(voltage):.3f} V")

        # Uncomment to plot the waveform
        # plt.figure(figsize=(10, 6))
        # plt.plot(time * 1e3, voltage)  # Convert time to ms
        # plt.xlabel('Time (ms)')
        # plt.ylabel('Voltage (V)')
        # plt.title('Oscilloscope Waveform - Channel 1')
        # plt.grid(True)
        # plt.show()


def measurements_example():
    """Example of making automated measurements."""
    print("\n" + "=" * 60)
    print("Automated Measurements Example")
    print("=" * 60)

    resource_string = "TCPIP0::192.168.1.100::INSTR"

    with DSOX4034A(resource_string) as scope:
        # Enable channel 1
        scope.channel_on(1)

        # Autoscale for easier setup
        scope.autoscale()

        # Make various measurements
        print("\nMeasurements on Channel 1:")
        print("-" * 40)

        try:
            vpp = scope.measure_vpp(1)
            print(f"Peak-to-Peak: {vpp:.3f} V")
        except:
            print("Peak-to-Peak: N/A")

        try:
            vmax = scope.measure_vmax(1)
            print(f"Maximum: {vmax:.3f} V")
        except:
            print("Maximum: N/A")

        try:
            vmin = scope.measure_vmin(1)
            print(f"Minimum: {vmin:.3f} V")
        except:
            print("Minimum: N/A")

        try:
            vavg = scope.measure_vavg(1)
            print(f"Average: {vavg:.3f} V")
        except:
            print("Average: N/A")

        try:
            vrms = scope.measure_vrms(1)
            print(f"RMS: {vrms:.3f} V")
        except:
            print("RMS: N/A")

        try:
            freq = scope.measure_frequency(1)
            print(f"Frequency: {freq:.3f} Hz")
        except:
            print("Frequency: N/A")

        try:
            period = scope.measure_period(1)
            print(f"Period: {period:.6e} s")
        except:
            print("Period: N/A")


def multi_channel_example():
    """Example of working with multiple channels."""
    print("\n" + "=" * 60)
    print("Multi-Channel Example")
    print("=" * 60)

    resource_string = "TCPIP0::192.168.1.100::INSTR"

    with DSOX4034A(resource_string) as scope:
        # Enable multiple channels
        for ch in [1, 2, 3, 4]:
            scope.channel_on(ch)
            scope.set_channel_scale(ch, 1.0)
            print(f"Channel {ch} enabled, scale: 1 V/div")

        # Acquire waveforms from multiple channels
        print("\nAcquiring waveforms from all channels...")
        scope.digitize([1, 2, 3, 4])

        waveforms = {}
        for ch in [1, 2, 3, 4]:
            time, voltage = scope.get_waveform(channel=ch, points=500)
            waveforms[ch] = (time, voltage)
            print(f"Channel {ch}: {len(voltage)} points, "
                  f"avg = {np.mean(voltage):.3f} V")


def list_resources_example():
    """List all available VISA resources."""
    print("\n" + "=" * 60)
    print("Available VISA Resources")
    print("=" * 60)

    import pyvisa
    rm = pyvisa.ResourceManager('@py')
    resources = rm.list_resources()

    if resources:
        print(f"Found {len(resources)} resource(s):")
        for res in resources:
            print(f"  - {res}")
    else:
        print("No VISA resources found")

    rm.close()


if __name__ == "__main__":
    """
    Main function - uncomment the examples you want to run.

    IMPORTANT: Update the resource_string in each example to match your
    oscilloscope's actual address before running!
    """

    print("DSOX4034A Oscilloscope Control Examples")
    print("=" * 60)
    print("\nNOTE: Update resource_string in each example before running!")
    print("      (Use list_resources_example() to find your device)")
    print()

    # Uncomment the examples you want to run:

    # List available VISA resources first
    list_resources_example()

    # Basic examples (comment out if you don't have a scope connected)
    # basic_connection_example()
    # context_manager_example()
    # channel_configuration_example()
    # trigger_configuration_example()
    # waveform_acquisition_example()
    # measurements_example()
    # multi_channel_example()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
