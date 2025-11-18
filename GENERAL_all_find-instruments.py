"""
Find VISA Instruments

This script lists all available VISA instruments connected to the system.
Supports USB, TCPIP (Ethernet), and other VISA interfaces.

For USB devices to be detected with pyvisa-py, you need:
1. pyusb package: pip install pyusb
2. USB backend: pip install libusb-package (or install libusb manually)
3. On Windows: May need Zadig to install WinUSB/libusb driver for the device
   Download from: https://zadig.akeo.ie/
"""

import pyvisa
import sys

def find_instruments():
    """Find and list all available VISA instruments."""
    print("="*60)
    print("VISA Instrument Finder")
    print("="*60)

    # Try pyvisa-py backend first
    print("\nUsing PyVISA-py backend (@py)...")
    try:
        rm = pyvisa.ResourceManager('@py')
        resources = rm.list_resources()

        if resources:
            print(f"\nFound {len(resources)} instrument(s):\n")
            for i, resource in enumerate(resources, 1):
                print(f"  {i}. {resource}")
                # Try to get instrument ID
                try:
                    inst = rm.open_resource(resource)
                    inst.timeout = 2000
                    idn = inst.query("*IDN?").strip()
                    print(f"     ID: {idn}")
                    inst.close()
                except Exception as e:
                    print(f"     (Could not query ID: {e})")
        else:
            print("\nNo instruments found.")
            print("\nTroubleshooting for USB devices:")
            print("  1. Check USB cable connection")
            print("  2. Install pyusb: pip install pyusb")
            print("  3. Install libusb: pip install libusb-package")
            print("  4. On Windows, use Zadig (https://zadig.akeo.ie/) to install")
            print("     WinUSB or libusb-win32 driver for your instrument")
            print("  5. Make sure the device is powered on")

        rm.close()

    except Exception as e:
        print(f"\nError with pyvisa-py backend: {e}")
        print("\nTrying to check USB support...")

        # Check for pyusb
        try:
            import usb.core
            print("  - pyusb is installed")

            # Try to find any USB devices
            devices = list(usb.core.find(find_all=True))
            if devices:
                print(f"  - Found {len(devices)} USB device(s)")
                print("\n  USB devices (may include non-instrument devices):")
                for dev in devices:
                    try:
                        print(f"    VID:PID = {dev.idVendor:04x}:{dev.idProduct:04x}")
                    except:
                        pass
            else:
                print("  - No USB devices found by pyusb")
                print("  - You may need to install libusb driver")
        except ImportError:
            print("  - pyusb is NOT installed")
            print("  - Install with: pip install pyusb")
        except Exception as usb_err:
            print(f"  - USB error: {usb_err}")
            print("  - You may need to install libusb backend")
            print("  - Try: pip install libusb-package")

    print("\n" + "="*60)

if __name__ == "__main__":
    find_instruments()