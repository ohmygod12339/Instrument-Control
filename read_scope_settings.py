"""
Read Current Oscilloscope Settings

This script connects to your oscilloscope and reads all current settings
including trigger, vertical scale, horizontal scale, and measurement configuration.

Usage:
    python read_scope_settings.py
"""

from instruments.keysight.dsox4034a import DSOX4034A
import time

# Your oscilloscope address
RESOURCE_STRING = "TCPIP::192.168.2.60::INSTR"


def read_all_settings(scope):
    """Read and display all current oscilloscope settings."""

    print("="*70)
    print("OSCILLOSCOPE SETTINGS")
    print("="*70)

    # Instrument identification
    print("\n[INSTRUMENT IDENTIFICATION]")
    print(f"ID: {scope.identify()}")

    # Acquisition mode
    print("\n[ACQUISITION MODE]")
    try:
        acquire_type = scope.query(":ACQ:TYPE?")
        print(f"Acquire Type: {acquire_type}")

        acquire_mode = scope.query(":ACQ:MODE?")
        print(f"Acquire Mode: {acquire_mode}")

        acquire_count = scope.query(":ACQ:COUN?")
        print(f"Acquire Count: {acquire_count}")

        # Check if running or stopped
        operand_register = scope.query(":OPER:COND?")
        print(f"Operational Condition: {operand_register}")
    except Exception as e:
        print(f"Error reading acquisition: {e}")

    # Channel settings for all channels
    for ch in [1, 2, 3, 4]:
        print(f"\n[CHANNEL {ch}]")
        try:
            is_on = scope.is_channel_on(ch)
            print(f"Display: {'ON' if is_on else 'OFF'}")

            if is_on:
                scale = scope.get_channel_scale(ch)
                print(f"Vertical Scale: {scale} V/div")

                offset = scope.get_channel_offset(ch)
                print(f"Vertical Offset: {offset} V")

                coupling = scope.get_channel_coupling(ch)
                print(f"Coupling: {coupling}")

                probe = scope.query(f":CHAN{ch}:PROB?")
                print(f"Probe Attenuation: {probe}")

                bwlimit = scope.query(f":CHAN{ch}:BWL?")
                print(f"Bandwidth Limit: {bwlimit}")
        except Exception as e:
            print(f"Error reading channel {ch}: {e}")

    # Timebase settings
    print("\n[TIMEBASE (HORIZONTAL)]")
    try:
        scale = scope.get_timebase_scale()
        print(f"Horizontal Scale: {scale} s/div")

        position = scope.get_timebase_position()
        print(f"Horizontal Position: {position} s")

        mode = scope.query(":TIM:MODE?")
        print(f"Timebase Mode: {mode}")

        reference = scope.query(":TIM:REF?")
        print(f"Reference: {reference}")
    except Exception as e:
        print(f"Error reading timebase: {e}")

    # Trigger settings
    print("\n[TRIGGER]")
    try:
        mode = scope.get_trigger_mode()
        print(f"Trigger Mode: {mode}")

        source = scope.get_trigger_source()
        print(f"Trigger Source: {source}")

        level = scope.get_trigger_level()
        print(f"Trigger Level: {level} V")

        slope = scope.get_trigger_slope()
        print(f"Trigger Slope: {slope}")

        sweep = scope.query(":TRIG:SWE?")
        print(f"Trigger Sweep: {sweep}")

        coupling = scope.query(":TRIG:EDGE:COUP?")
        print(f"Trigger Coupling: {coupling}")
    except Exception as e:
        print(f"Error reading trigger: {e}")

    # Measurement settings
    print("\n[MEASUREMENTS]")
    try:
        # Check if any measurements are displayed
        for i in range(1, 6):  # Check measurement slots 1-5
            try:
                source = scope.query(f":MEAS:SOUR{i}?")
                if source and source != "NONE":
                    print(f"Measurement {i} Source: {source}")
            except:
                pass

        # Check measurement statistics
        stats = scope.query(":MEAS:STAT?")
        print(f"Statistics Display: {stats}")

    except Exception as e:
        print(f"Error reading measurements: {e}")

    # Waveform settings
    print("\n[WAVEFORM ACQUISITION]")
    try:
        source = scope.query(":WAV:SOUR?")
        print(f"Waveform Source: {source}")

        format = scope.query(":WAV:FORM?")
        print(f"Waveform Format: {format}")

        points_mode = scope.query(":WAV:POIN:MODE?")
        print(f"Points Mode: {points_mode}")

        points = scope.query(":WAV:POIN?")
        print(f"Points: {points}")
    except Exception as e:
        print(f"Error reading waveform settings: {e}")

    # Test measurement speed
    print("\n[MEASUREMENT SPEED TEST]")
    print("Testing VRMS measurement speed...")

    try:
        # Time a single VRMS measurement
        start = time.time()
        vrms = scope.measure_vrms(channel=1)
        elapsed = time.time() - start

        print(f"Channel 1 VRMS: {vrms:.6f} V")
        print(f"Measurement time: {elapsed:.3f} seconds")

        # Try multiple measurements
        print("\nTiming 5 consecutive measurements:")
        times = []
        for i in range(5):
            start = time.time()
            vrms = scope.measure_vrms(channel=1)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  {i+1}. VRMS: {vrms:.6f} V, Time: {elapsed:.3f}s")

        avg_time = sum(times) / len(times)
        print(f"\nAverage measurement time: {avg_time:.3f} seconds")

        if avg_time > 0.5:
            print("\n⚠ WARNING: Measurements are very slow (>0.5s)")
            print("Possible causes:")
            print("  - Timebase is set too slow (long acquisition time)")
            print("  - Scope is waiting for trigger")
            print("  - Averaging or envelope mode enabled")

    except Exception as e:
        print(f"Error testing measurement speed: {e}")

    print("\n" + "="*70)


def main():
    """Main function."""
    print("Connecting to oscilloscope...")
    print(f"Address: {RESOURCE_STRING}\n")

    scope = DSOX4034A(RESOURCE_STRING)

    try:
        scope.connect()
        print("Connected successfully!\n")

        read_all_settings(scope)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        scope.disconnect()


if __name__ == "__main__":
    main()
