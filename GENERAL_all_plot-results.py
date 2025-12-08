"""
General Purpose Result Plotter

This script reads Excel result files and plots measurements with:
- X-axis: Elapsed Time (hr)
- Y-axis: Measurement values (Vrms, Temperature, etc.)

Supports dual y-axes for measurements with different scales.

Usage:
    # Plot all measurements from a file
    python GENERAL_all_plot-results.py results/Result_20251118_150710_Real-Time-Result_FINAL.xlsx

    # Plot specific columns
    python GENERAL_all_plot-results.py results/file.xlsx --columns "Vrms CH1 (V)" "Temperature (C)"

    # List available files
    python GENERAL_all_plot-results.py --list

    # Use dual y-axis (for different scales)
    python GENERAL_all_plot-results.py results/file.xlsx --dual-axis

    # Use dual y-axis with custom labels
    python GENERAL_all_plot-results.py results/file.xlsx --dual-axis --ylabel-left "Voltage (V)" --ylabel-right "Temperature (°C)"

Requirements:
    pip install matplotlib pandas openpyxl
"""

import sys
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import argparse


def list_result_files(results_dir: str = "results") -> list:
    """List all Excel result files in the results directory."""
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"Results directory not found: {results_dir}")
        return []

    files = sorted(results_path.glob("*.xlsx"))
    return files


def read_result_file(filepath: str) -> pd.DataFrame:
    """
    Read Excel result file into a DataFrame.

    Args:
        filepath: Path to the Excel file

    Returns:
        DataFrame with measurement data
    """
    df = pd.read_excel(filepath)
    return df


def get_measurement_columns(df: pd.DataFrame) -> list:
    """
    Get list of measurement columns (excluding Timestamp and Elapsed Time).

    Args:
        df: DataFrame with result data

    Returns:
        List of measurement column names
    """
    exclude = ['Timestamp', 'Elapsed Time (ms)', 'Elapsed Time (hr)']
    return [col for col in df.columns if col not in exclude]


def calculate_axis_limits(data, headroom_percent: float = 10):
    """
    Calculate axis limits with headroom.

    Args:
        data: Series or array of values
        headroom_percent: Percentage of headroom to add (default 10%)

    Returns:
        Tuple of (min_limit, max_limit)
    """
    data_min = data.min()
    data_max = data.max()
    data_range = data_max - data_min

    # Handle case where all values are the same
    if data_range == 0:
        data_range = abs(data_min) * 0.1 if data_min != 0 else 1

    headroom = data_range * (headroom_percent / 100)

    return (data_min - headroom, data_max + headroom)


def plot_results(df: pd.DataFrame, columns: list = None, dual_axis: bool = False,
                title: str = None, save_path: str = None, ylabel_left: str = None,
                ylabel_right: str = None):
    """
    Plot measurement results.

    Args:
        df: DataFrame with result data
        columns: List of columns to plot (None for all measurements)
        dual_axis: Use dual y-axes for different scales
        title: Plot title
        save_path: Path to save the plot image
        ylabel_left: Custom label for left y-axis (dual-axis mode only)
        ylabel_right: Custom label for right y-axis (dual-axis mode only)
    """
    # Get elapsed time column
    if 'Elapsed Time (hr)' not in df.columns:
        print("Error: 'Elapsed Time (hr)' column not found")
        return

    x_data = df['Elapsed Time (hr)']

    # Get measurement columns
    all_measurements = get_measurement_columns(df)
    if not all_measurements:
        print("Error: No measurement columns found")
        return

    # Use specified columns or all measurements
    if columns:
        plot_columns = [col for col in columns if col in df.columns]
        if not plot_columns:
            print(f"Error: None of the specified columns found")
            print(f"Available columns: {all_measurements}")
            return
    else:
        plot_columns = all_measurements

    # Create figure
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Color cycle
    colors = plt.cm.tab10.colors

    if dual_axis and len(plot_columns) >= 2:
        # Dual y-axis mode: first column on left, rest on right
        # Plot first column on left axis
        col1 = plot_columns[0]
        line1 = ax1.plot(x_data, df[col1], color=colors[0], linewidth=1,
                        label=col1, marker='', linestyle='-')
        ax1.set_xlabel('Elapsed Time (hr)', fontsize=12)

        # Use custom label if provided, otherwise use column name
        left_label = ylabel_left if ylabel_left else col1
        ax1.set_ylabel(left_label, color=colors[0], fontsize=12)
        ax1.tick_params(axis='y', labelcolor=colors[0])

        # Scale left y-axis to data range with headroom
        y1_min, y1_max = calculate_axis_limits(df[col1])
        ax1.set_ylim(y1_min, y1_max)

        # Create second y-axis
        ax2 = ax1.twinx()

        # Plot remaining columns on right axis
        lines = line1
        for i, col in enumerate(plot_columns[1:], 1):
            line = ax2.plot(x_data, df[col], color=colors[i % len(colors)],
                           linewidth=1, label=col, marker='', linestyle='-')
            lines += line

        if len(plot_columns) == 2:
            # Use custom label if provided, otherwise use column name
            right_label = ylabel_right if ylabel_right else plot_columns[1]
            ax2.set_ylabel(right_label, color=colors[1], fontsize=12)
            ax2.tick_params(axis='y', labelcolor=colors[1])

            # Scale right y-axis to data range with headroom
            y2_min, y2_max = calculate_axis_limits(df[plot_columns[1]])
            ax2.set_ylim(y2_min, y2_max)
        else:
            # Use custom label if provided, otherwise use generic label
            right_label = ylabel_right if ylabel_right else 'Other Measurements'
            ax2.set_ylabel(right_label, fontsize=12)

            # For multiple columns on right axis, find overall min/max
            all_right_data = pd.concat([df[col] for col in plot_columns[1:]])
            y2_min, y2_max = calculate_axis_limits(all_right_data)
            ax2.set_ylim(y2_min, y2_max)

        # Combined legend
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right')

        # Print scale information
        print(f"\nY-axis scaling:")
        print(f"  Left ({col1}): {y1_min:.4f} to {y1_max:.4f}")
        if len(plot_columns) == 2:
            print(f"  Right ({plot_columns[1]}): {y2_min:.4f} to {y2_max:.4f}")
        else:
            print(f"  Right (combined): {y2_min:.4f} to {y2_max:.4f}")

    else:
        # Single y-axis mode: all columns on same axis
        for i, col in enumerate(plot_columns):
            ax1.plot(x_data, df[col], color=colors[i % len(colors)],
                    linewidth=1, label=col, marker='', linestyle='-')

        ax1.set_xlabel('Elapsed Time (hr)', fontsize=12)
        ax1.set_ylabel('Measurement Value', fontsize=12)
        ax1.legend(loc='upper right')

    # Set title
    if title:
        plt.title(title, fontsize=14)
    else:
        plt.title('Measurement Results', fontsize=14)

    # Grid and styling
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_minor_locator(AutoMinorLocator())
    ax1.yaxis.set_minor_locator(AutoMinorLocator())

    # Adjust layout
    plt.tight_layout()

    # Save or show
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()

    plt.close()


def plot_subplots(df: pd.DataFrame, columns: list = None, title: str = None,
                 save_path: str = None):
    """
    Plot each measurement in separate subplots.

    Args:
        df: DataFrame with result data
        columns: List of columns to plot (None for all measurements)
        title: Plot title
        save_path: Path to save the plot image
    """
    if 'Elapsed Time (hr)' not in df.columns:
        print("Error: 'Elapsed Time (hr)' column not found")
        return

    x_data = df['Elapsed Time (hr)']

    # Get measurement columns
    all_measurements = get_measurement_columns(df)
    if columns:
        plot_columns = [col for col in columns if col in df.columns]
    else:
        plot_columns = all_measurements

    if not plot_columns:
        print("Error: No columns to plot")
        return

    # Create subplots
    n_plots = len(plot_columns)
    fig, axes = plt.subplots(n_plots, 1, figsize=(12, 3 * n_plots), sharex=True)

    if n_plots == 1:
        axes = [axes]

    colors = plt.cm.tab10.colors

    for i, col in enumerate(plot_columns):
        ax = axes[i]
        ax.plot(x_data, df[col], color=colors[i % len(colors)],
               linewidth=1, marker='', linestyle='-')
        ax.set_ylabel(col, fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_minor_locator(AutoMinorLocator())

    # Set x-label on bottom subplot
    axes[-1].set_xlabel('Elapsed Time (hr)', fontsize=12)
    axes[-1].xaxis.set_minor_locator(AutoMinorLocator())

    # Set title
    if title:
        fig.suptitle(title, fontsize=14)
    else:
        fig.suptitle('Measurement Results', fontsize=14)

    plt.tight_layout()

    # Save or show
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()

    plt.close()


def print_file_info(filepath: str):
    """Print information about the result file."""
    df = read_result_file(filepath)

    print(f"\nFile: {filepath}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    measurements = get_measurement_columns(df)
    print(f"\nMeasurement columns:")
    for col in measurements:
        print(f"  - {col}")

    if 'Elapsed Time (hr)' in df.columns:
        elapsed = df['Elapsed Time (hr)']
        print(f"\nTime range: {elapsed.min():.4f} hr to {elapsed.max():.4f} hr")
        print(f"Duration: {elapsed.max() - elapsed.min():.4f} hours")


def main():
    parser = argparse.ArgumentParser(
        description='Plot measurement results from Excel files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available result files
  python GENERAL_all_plot-results.py --list

  # Plot all measurements from a file
  python GENERAL_all_plot-results.py results/Result_FINAL.xlsx

  # Plot specific columns
  python GENERAL_all_plot-results.py results/file.xlsx -c "Watts (W)" "kWh"

  # Use dual y-axis for different scales
  python GENERAL_all_plot-results.py results/file.xlsx --dual-axis

  # Use dual y-axis with custom labels
  python GENERAL_all_plot-results.py results/file.xlsx --dual-axis --ylabel-left "Voltage (V)" --ylabel-right "Temperature (°C)"

  # Plot in separate subplots
  python GENERAL_all_plot-results.py results/file.xlsx --subplots

  # Plot specific columns with dual y-axis and custom labels
  python GENERAL_all_plot-results.py results/file.xlsx --dual-axis -c "Vrms (V)" "Temp Ch1 (°C)" --yl "Voltage" --yr "Temperature"

  # Save plot to file
  python GENERAL_all_plot-results.py results/file.xlsx -o output.png
        """
    )

    parser.add_argument('filepath', nargs='?', help='Path to Excel result file')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available result files')
    parser.add_argument('--columns', '-c', nargs='+',
                       help='Specific columns to plot')
    parser.add_argument('--dual-axis', '-d', action='store_true',
                       help='Use dual y-axes for different scales')
    parser.add_argument('--ylabel-left', '--yl', metavar='LABEL',
                       help='Custom label for left y-axis (use with --dual-axis)')
    parser.add_argument('--ylabel-right', '--yr', metavar='LABEL',
                       help='Custom label for right y-axis (use with --dual-axis)')
    parser.add_argument('--subplots', '-s', action='store_true',
                       help='Plot each measurement in separate subplots')
    parser.add_argument('--output', '-o', help='Save plot to file')
    parser.add_argument('--title', '-t', help='Plot title')
    parser.add_argument('--info', '-i', action='store_true',
                       help='Show file information only')

    args = parser.parse_args()

    # List result files
    if args.list:
        files = list_result_files()
        if files:
            print("\nAvailable result files:\n")
            for f in files:
                size = f.stat().st_size / 1024
                print(f"  {f.name} ({size:.1f} KB)")
        else:
            print("No result files found in results/ directory")
        return

    # Check if filepath provided
    if not args.filepath:
        parser.print_help()
        return

    # Check file exists
    if not os.path.exists(args.filepath):
        print(f"Error: File not found: {args.filepath}")
        return

    # Show file info
    if args.info:
        print_file_info(args.filepath)
        return

    # Read data
    print(f"Reading: {args.filepath}")
    df = read_result_file(args.filepath)

    # Generate title from filename if not provided
    title = args.title
    if not title:
        filename = Path(args.filepath).stem
        title = filename.replace('_', ' ')

    # Plot
    if args.subplots:
        plot_subplots(df, columns=args.columns, title=title, save_path=args.output)
    else:
        plot_results(df, columns=args.columns, dual_axis=args.dual_axis,
                    title=title, save_path=args.output,
                    ylabel_left=args.ylabel_left, ylabel_right=args.ylabel_right)


if __name__ == "__main__":
    main()
