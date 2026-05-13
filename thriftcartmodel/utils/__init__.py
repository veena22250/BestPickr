"""
Utility modules for the ThrifCart application.

This package contains various utility modules that provide helper functions
and classes used throughout the ThrifCart application.

Modules:
    data_loader: Provides data loading, preprocessing, and synthetic data generation.
"""

# Import key components to make them available at the package level
from .data_loader import DataLoader

__all__ = ['DataLoader']
__version__ = '0.1.0'
