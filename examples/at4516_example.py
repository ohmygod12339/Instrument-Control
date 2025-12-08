"""
Anbai AT4516 Temperature Meter - Example Usage

This script demonstrates basic usage of the AT4516 temperature meter control module.

Requirements:
    - pyserial installed (pip install pyserial)
    - AT4516 connected via RS-232 (USB-Serial adapter or direct COM port)
    - Correct COM port configured

Author: Claude Code
Date: 2025-12-05
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from instruments.anbai import AT4516


def basic_usage_example():
    """Basic example: Connect and read temperature from all channels."""
    print("=" * 60)
    print("AT4516 Basic Usage Example")
    print("=" * 60)

    # Create instance (use default COM port or specify your own)
    # temp_meter = AT4516(port='COM5', baudrate=115200)
    temp_meter = AT4516()  # Uses DEFAULT_PORT

    try:
        # Connect to instrument
        print("\n1. Connecting to instrument...")
        temp_meter.connect()

        # Get instrument information
        print("\n2. Querying instrument information...")
        idn = temp_meter.identify()
        print(f"   Instrument ID: {idn}")

        # Configure instrument (CRITICAL: Use this method for proper initialization!)
        print("\n3. Configuring instrument...")
        temp_meter.configure_and_start(tc_type='TC-K', rate='FAST', unit='CEL')

        # Verify configuration
        print("\n4. Verifying configuration...")
        tc_type = temp_meter.get_thermocouple_type()
        rate = temp_meter.get_sampling_rate()
        unit = temp_meter.get_temperature_unit()
        print(f"   Thermocouple type: {tc_type}")
        print(f"   Sampling rate: {rate}")
        print(f"   Unit: {unit}")

        # Read all channels
        print("\n5. Reading all channels...")
        temps = temp_meter.read_all_channels()
        print(f"   All channels: {temps}")

        # Read specific channels
        print("\n6. Reading individual channels...")
        for i in range(1, 9):
            temp = temp_meter.read_channel(i)
            if temp is not None and temp > -100000:
                print(f"   Channel {i}: {temp:.1f}°C")
            else:
                print(f"   Channel {i}: Disabled or Error")

        # Check for errors
        print("\n7. Checking for errors...")
        error = temp_meter.check_error()
        print(f"   Error status: {error}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Disconnect
        print("\n8. Disconnecting...")
        temp_meter.disconnect()

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


def continuous_monitoring_example():
    """Example: Continuously monitor temperature from all channels."""
    print("=" * 60)
    print("AT4516 Continuous Monitoring Example")
    print("=" * 60)
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)

    temp_meter = AT4516()

    try:
        # Connect
        temp_meter.connect()

        # Configure instrument (use helper method for proper initialization)
        temp_meter.configure_and_start(tc_type='TC-K', rate='FAST', unit='CEL')

        # Continuous monitoring loop
        print("\nTimestamp        Ch1     Ch2     Ch3     Ch4     Ch5     Ch6     Ch7     Ch8")
        print("-" * 90)

        while True:
            # Read all channels
            temps = temp_meter.read_all_channels()

            # Format timestamp
            timestamp = time.strftime("%H:%M:%S")

            # Format temperature values
            temp_strs = []
            for temp in temps:
                if temp is not None:
                    temp_strs.append(f"{temp:6.1f}")
                else:
                    temp_strs.append("   N/A")

            # Print results
            print(f"{timestamp}    " + "  ".join(temp_strs))

            # Wait before next reading
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Stop measurement and disconnect
        try:
            temp_meter.stop_measurement()
        except:
            pass
        temp_meter.disconnect()


def comparator_example():
    """Example: Use comparator function for limit checking."""
    print("=" * 60)
    print("AT4516 Comparator (Limit Checking) Example")
    print("=" * 60)

    temp_meter = AT4516()

    try:
        # Connect
        temp_meter.connect()

        # Configure instrument (use helper method)
        temp_meter.configure_and_start(tc_type='TC-K', rate='FAST', unit='CEL')

        # Set temperature limits
        print("\n1. Setting temperature limits...")
        temp_meter.set_low_limit(20.0)   # Low limit: 20°C
        temp_meter.set_high_limit(30.0)  # High limit: 30°C
        print("   Low limit: 20.0°C")
        print("   High limit: 30.0°C")

        # Set specific limits for Channel 1
        print("\n2. Setting Channel 1 specific limits...")
        temp_meter.set_channel_low_limit(1, 22.0)
        temp_meter.set_channel_high_limit(1, 28.0)
        print("   Channel 1 Low: 22.0°C")
        print("   Channel 1 High: 28.0°C")

        # Enable comparator
        print("\n3. Enabling comparator...")
        temp_meter.enable_comparator()
        print(f"   Comparator enabled: {temp_meter.get_comparator_status()}")

        # Enable beep for limit violations
        print("\n4. Enabling beep...")
        temp_meter.enable_beep()
        print(f"   Beep enabled: {temp_meter.get_beep_status()}")

        # Read temperatures
        print("\n5. Reading temperatures (comparator active)...")
        temps = temp_meter.read_all_channels()
        for i, temp in enumerate(temps, start=1):
            if temp is not None:
                status = ""
                if temp < 20.0:
                    status = " [BELOW LOW LIMIT]"
                elif temp > 30.0:
                    status = " [ABOVE HIGH LIMIT]"
                else:
                    status = " [OK]"
                print(f"   Channel {i}: {temp:.1f}°C {status}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Disconnect
        temp_meter.disconnect()


def context_manager_example():
    """Example: Use context manager for automatic connection management."""
    print("=" * 60)
    print("AT4516 Context Manager Example")
    print("=" * 60)

    # Using 'with' statement for automatic connect/disconnect
    with AT4516() as temp_meter:
        # Configure instrument (use helper method)
        temp_meter.configure_and_start(tc_type='TC-K', rate='FAST', unit='CEL')

        # Read temperatures
        print("\nReading temperatures:")
        for i in range(1, 9):
            temp = temp_meter.read_channel(i)
            if temp is not None:
                print(f"  Channel {i}: {temp:.1f}°C")

    # Connection automatically closed when exiting 'with' block
    print("\nContext manager automatically disconnected")


def list_ports_example():
    """Example: List all available COM ports."""
    print("=" * 60)
    print("Available COM Ports")
    print("=" * 60)

    ports = AT4516.list_available_ports()

    if ports:
        print("\nFound the following COM ports:")
        for i, port in enumerate(ports, start=1):
            print(f"  {i}. {port}")
    else:
        print("\nNo COM ports found!")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run examples
    print("\n" * 2)

    # Uncomment the example you want to run:

    # Example 1: Basic usage
    basic_usage_example()

    # Example 2: List available COM ports
    # list_ports_example()

    # Example 3: Continuous monitoring
    # continuous_monitoring_example()

    # Example 4: Comparator (limit checking)
    # comparator_example()

    # Example 5: Context manager
    # context_manager_example()
