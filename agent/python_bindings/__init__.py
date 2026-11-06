"""
Bibliotheque Python bindings for the C++ library system.

This package provides Python interface to the C++ Bibliothèque Library System
using pybind11 selective bindings approach.
"""

# Make classes available at module level
from .bibliotheque import Book, User, Library, FileManager, create_library

__all__ = ['Book', 'User', 'Library', 'FileManager', 'create_library']
__version__ = "0.1.0"
