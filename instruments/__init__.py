"""
Instrument Control Package

This package provides Python modules for controlling laboratory instruments
via USB, Ethernet, or other communication interfaces using VISA and other protocols.
"""

__version__ = "0.1.0"
__author__ = "Lab Team"

# Import base classes
from .base_logger import BaseDataLogger

# Import instrument modules here as they are added
# from .keysight import DSOX4034A
# from .agilent import A34405A

__all__ = ['BaseDataLogger']
