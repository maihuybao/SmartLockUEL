"""Central path utilities for the SmartLocker UEL application.

Provides helper functions to resolve resource and data directories,
supporting both development environments and PyInstaller-bundled executables.
"""

import sys
import os


def resource_dir():
    """Return the directory containing bundled resources (ui/, images/).

    When running as a PyInstaller onefile executable, resources are extracted
    to a temporary directory referenced by ``sys._MEIPASS``. In development
    mode, the project root directory is returned.

    Returns:
        str: The absolute path to the resource directory.
    """
    if getattr(sys, "_MEIPASS", None):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def data_dir():
    """Return the directory for persistent data files (datasets/).

    When running as a frozen PyInstaller executable, the directory containing
    the executable is returned. In development mode, the project root
    directory is returned.

    Returns:
        str: The absolute path to the data directory.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
