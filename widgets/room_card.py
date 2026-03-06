"""Helper to create room cards with session status indicators."""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSizePolicy,
)
from PyQt6.QtCore import Qt
from models.booking_model import get_bookings_by_room

STATUS_COLORS = {
    "Available": "#4CAF50",
    "Occupied": "#F44336",
    "Full": "#FF9800",
    "Cleaning": "#2196F3",
}

SESSIONS = [
    ("Session 1", "07:00 – 09:30"),
    ("Session 2", "09:45 – 12:15"),
    ("Session 3", "12:30 – 15:00"),
    ("Session 4", "15:15 – 17:45"),
]


def create_room_card(room):
    # Get bookings to check session status
    bookings = get_bookings_by_room(room["id"])
    smap = {b["session"]: b["status"] for b in bookings}

    # Auto-detect Full: if all 4 sessions are booked
    booked_count = 0
    for name, tr in SESSIONS:
        key = f"{name} ({tr})"
        if smap.get(key) in ("Pending", "Approved"):
            booked_count += 1
    display_status = "Full" if booked_count == 4 else room["status"]

    color = STATUS_COLORS.get(display_status, "#9E9E9E")
    card = QWidget()
    card.setMinimumSize(200, 175)
    card.setMaximumHeight(220)
    card.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
    )
    card.setStyleSheet(
        f"background:white;border:2px solid {color};border-radius:10px;"
    )
    vbox = QVBoxLayout(card)
    vbox.setContentsMargins(10, 8, 10, 6)
    vbox.setSpacing(3)

    lbl_id = QLabel(room["room_id"])
    lbl_id.setStyleSheet(
        "color:#333;font-weight:bold;font-size:14px;border:none;"
    )
    lbl_type = QLabel(f"{room['room_type']} - {room['capacity']} seats")
    lbl_type.setStyleSheet("color:#666;font-size:11px;border:none;")
    vbox.addWidget(lbl_id)
    vbox.addWidget(lbl_type)

    # Session status grid (2x2)
    sgrid = QGridLayout()
    sgrid.setSpacing(2)
    sgrid.setContentsMargins(0, 4, 0, 0)

    for i, (name, time_range) in enumerate(SESSIONS):
        key = f"{name} ({time_range})"
        bs = smap.get(key)
        if bs == "Approved":
            dot_c, txt = "#4CAF50", "Approved"
        elif bs == "Pending":
            dot_c, txt = "#FF9800", "Pending"
        else:
            dot_c, txt = "#E0E0E0", "Available"

        row = QHBoxLayout()
        row.setSpacing(3)
        row.setContentsMargins(0, 0, 0, 0)
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{dot_c};font-size:10px;border:none;")
        dot.setMaximumWidth(12)
        info = QLabel(f"{name}: {txt}")
        info.setStyleSheet("color:#555;font-size:9px;border:none;")
        row.addWidget(dot)
        row.addWidget(info)
        sgrid.addLayout(row, i // 2, i % 2)

    vbox.addLayout(sgrid)
    return card
