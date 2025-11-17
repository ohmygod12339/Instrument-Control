"""
Example: Real-Time Vrms Data Logger

This example demonstrates how to use the vrms_logger.py script to log
Channel 1 Vrms data from the Keysight DSOX4034A oscilloscope.

Setup:
1. Connect your DSOX4034A oscilloscope via USB or Ethernet
2. Find your instrument's VISA resource string (use pyvisa-info or NI MAX)
3. Run this script or the vrms_logger.py directly

Usage via command line:
    python vrms_logger.py "USB0::0x0957::0x17A6::MY12345678::INSTR"
    python vrms_logger.py "TCPIP0::192.168.1.100::INSTR"

Usage via Python import:
    See example code below
"""

from instruments.keysight.dsox4034a import DSOX4034A
import sys
import os

# Add parent directory to path to import vrms_logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vrms_logger import VrmsLogger


def example_usage():
    """
    Example of using VrmsLogger programmatically.
    """
    # Configure your oscilloscope resource string
    # USB format: "USB0::0x0957::0x17A6::MY########::INSTR"
    # TCPIP format: "TCPIP0::192.168.1.100::INSTR"

    # Replace with your actual resource string
    RESOURCE_STRING = "USB0::0x0957::0x17A6::MY12345678::INSTR"

    # Create logger instance
    logger = VrmsLogger(RESOURCE_STRING, results_dir="results")

    try:
        # Connect to oscilloscope
        logger.connect()

        # Setup Excel files
        logger.setup_excel_files()

        # Start logging (will run until Ctrl+C)
        logger.run()

    except KeyboardInterrupt:
        print("\n\nStopping logger...")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        logger.close()
        logger.disconnect()


def find_oscilloscope():
    """
    Helper function to find connected oscilloscopes.
    """
    import pyvisa

    print("Searching for connected instruments...")

    try:
        rm = pyvisa.ResourceManager('@py')
        resources = rm.list_resources()

        print(f"\nFound {len(resources)} instrument(s):")
        for resource in resources:
            print(f"  - {resource}")

            # Try to identify
            try:
                inst = rm.open_resource(resource)
                inst.timeout = 2000
                idn = inst.query("*IDN?")
                print(f"    ID: {idn.strip()}")
                inst.close()
            except:
                print(f"    (Could not identify)")

        rm.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Keysight DSOX4034A - Real-Time Vrms Logger Example")
    print("="*60)
    print()

    # Uncomment to search for connected instruments
    # find_oscilloscope()
    # print()

    print("To use this logger:")
    print("1. Edit this file and set your RESOURCE_STRING")
    print("2. Run: python vrms_logger_example.py")
    print()
    print("Or run directly from command line:")
    print('  python vrms_logger.py "USB0::0x0957::0x17A6::MY12345678::INSTR"')
    print()

    # Uncomment to run the example
    # example_usage()
