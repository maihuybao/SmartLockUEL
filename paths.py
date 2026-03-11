"""Duong dan trung tam cho ung dung.

- resource_dir(): thu muc chua ui/, images/ (bundle trong exe khi dong goi)
- data_dir(): thu muc chua datasets/ (nam ngoai exe, ben canh file .exe)
"""

import sys
import os


def resource_dir():
    """Thu muc chua tai nguyen bundle (ui, images).
    Khi dong goi onefile, PyInstaller giai nen vao _MEIPASS."""
    if getattr(sys, "_MEIPASS", None):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def data_dir():
    """Thu muc chua du lieu ngoai (datasets).
    Luon nam ben canh file exe (hoac thu muc project khi dev)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
