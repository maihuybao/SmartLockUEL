"""Helper to create room cards with session status indicators."""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt
from models.booking_model import get_bookings_by_room

STATUS_COLORS = {
    "Available": "#4CAF50",
    "Occupied": "#F44336",
    "Full": "#FF9800",
    "Cleaning": "#2196F3",
}

STATUS_BG = {
    "Available": "#E8F5E9",
    "Occupied": "#FFEBEE",
    "Full": "#FFF3E0",
    "Cleaning": "#E3F2FD",
}

SESSIONS = [
    ("Session 1", "07:00 – 09:30"),
    ("Session 2", "09:45 – 12:15"),
    ("Session 3", "12:30 – 15:00"),
    ("Session 4", "15:15 – 17:45"),
]


def get_display_status(room):
    bookings = get_bookings_by_room(room["id"])
    smap = {b["session"]: b["status"] for b in bookings}
    booked_count = sum(
        1 for name, tr in SESSIONS
        if smap.get(f"{name} ({tr})") in ("Pending", "Approved")
    )
    return "Full" if booked_count == 4 else room["status"]


def create_room_card(room):
    bookings = get_bookings_by_room(room["id"])
    smap = {b["session"]: b["status"] for b in bookings}

    booked_count = sum(
        1 for name, tr in SESSIONS
        if smap.get(f"{name} ({tr})") in ("Pending", "Approved")
    )
    display_status = "Full" if booked_count == 4 else room["status"]

    border_color = STATUS_COLORS.get(display_status, "#9E9E9E")
    badge_bg = STATUS_BG.get(display_status, "#F5F5F5")

    card = QWidget()
    card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    card.setMinimumWidth(160)
    card.setFixedHeight(110)
    card.setStyleSheet(
        f"QWidget#roomCard {{"
        f"  background: white;"
        f"  border: 2px solid {border_color};"
        f"  border-radius: 10px;"
        f"}}"
    )
    card.setObjectName("roomCard")

    vbox = QVBoxLayout(card)
    vbox.setContentsMargins(12, 10, 12, 10)
    vbox.setSpacing(6)

    # -- Header row: room ID + status badge --
    header = QHBoxLayout()
    header.setSpacing(6)

    lbl_id = QLabel(room["room_id"])
    lbl_id.setStyleSheet(
        "color:#1a1a2e;font-weight:bold;font-size:14px;border:none;"
    )

    lbl_status = QLabel(display_status)
    lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl_status.setFixedHeight(20)
    lbl_status.setStyleSheet(
        f"color:{border_color};"
        f"background:{badge_bg};"
        f"border:1px solid {border_color};"
        f"border-radius:9px;"
        f"font-size:10px;"
        f"font-weight:bold;"
        f"padding:0 7px;"
    )

    header.addWidget(lbl_id)
    header.addStretch()
    header.addWidget(lbl_status)
    vbox.addLayout(header)

    # -- Room type + capacity --
    lbl_type = QLabel(f"{room['room_type']}  ·  {room['capacity']} seats")
    lbl_type.setStyleSheet("color:#888;font-size:11px;border:none;")
    vbox.addWidget(lbl_type)

    # -- Divider --
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color:#F0F0F0;border:none;background:#F0F0F0;max-height:1px;")
    vbox.addWidget(line)

    # -- Session dots row --
    srow = QHBoxLayout()
    srow.setSpacing(8)
    srow.setContentsMargins(0, 0, 0, 0)
    srow.addStretch()

    for name, time_range in SESSIONS:
        key = f"{name} ({time_range})"
        bs = smap.get(key)
        if bs == "Approved":
            dot_c = "#4CAF50"
        elif bs == "Pending":
            dot_c = "#FF9800"
        else:
            dot_c = "#D0D0D0"

        dot = QLabel("●")
        dot.setStyleSheet(f"color:{dot_c};font-size:15px;border:none;")
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dot.setToolTip(f"{name} ({time_range}): {bs or 'Available'}")
        srow.addWidget(dot)

    srow.addStretch()
    vbox.addLayout(srow)

    return card
