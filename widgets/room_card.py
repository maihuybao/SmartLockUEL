"""Helper to create room cards with booking status indicators."""
from datetime import date as _date
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt
from models.booking_model import get_bookings_by_room_date

OP_START = 6 * 60   # 06:00
OP_END   = 22 * 60  # 22:00

STATUS_COLORS = {
    "Available": "#4CAF50",
    "Occupied":  "#F44336",
    "Full":      "#FF9800",
}

STATUS_BG = {
    "Available": "#E8F5E9",
    "Occupied":  "#FFEBEE",
    "Full":      "#FFF3E0",
}


def _to_minutes(t):
    h, m = map(int, t.strip().split(":"))
    return h * 60 + m


def _is_full_today(room_pk):
    """Return True if every 30-min slot in 06:00-22:00 is covered today."""
    today = _date.today().strftime("%Y-%m-%d")
    bookings = get_bookings_by_room_date(room_pk, today)

    booked = set()
    for b in bookings:
        start = max(_to_minutes(b["time_start"]), OP_START)
        end   = min(_to_minutes(b["time_end"]), OP_END)
        for slot in range(start, end, 30):
            booked.add(slot)

    all_slots = set(range(OP_START, OP_END, 30))
    return all_slots.issubset(booked)


def get_display_status(room):
    if room["status"] == "Available" and _is_full_today(room["id"]):
        return "Full"
    return room["status"]


def create_room_card(room, on_context=None):
    display_status = get_display_status(room)
    border_color = STATUS_COLORS.get(display_status, "#9E9E9E")
    badge_bg     = STATUS_BG.get(display_status, "#F5F5F5")

    from models.booking_model import get_bookings_by_room
    bookings = get_bookings_by_room(room["id"])
    active_count = len(bookings)

    card = QWidget()
    card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    card.setFixedSize(200, 110)
    card.setStyleSheet(
        f"QWidget#roomCard {{"
        f"  background: white;"
        f"  border: 2px solid {border_color};"
        f"  border-radius: 10px;"
        f"}}"
    )
    card.setObjectName("roomCard")

    if on_context:
        card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda pos: on_context(room, card.mapToGlobal(pos))
        )

    vbox = QVBoxLayout(card)
    vbox.setContentsMargins(12, 10, 12, 10)
    vbox.setSpacing(6)

    header = QHBoxLayout()
    header.setSpacing(6)

    lbl_id = QLabel(room["room_id"])
    lbl_id.setStyleSheet("color:#1a1a2e;font-weight:bold;font-size:14px;border:none;")

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

    lbl_type = QLabel(f"{room['room_type']}  ·  {room['capacity']} seats")
    lbl_type.setStyleSheet("color:#888;font-size:11px;border:none;")
    vbox.addWidget(lbl_type)

    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color:#F0F0F0;border:none;background:#F0F0F0;max-height:1px;")
    vbox.addWidget(line)

    if active_count > 0:
        lbl_bookings = QLabel(f"{active_count} active booking{'s' if active_count > 1 else ''}")
        lbl_bookings.setStyleSheet("color:#FF9800;font-size:11px;border:none;")
    else:
        lbl_bookings = QLabel("No active bookings")
        lbl_bookings.setStyleSheet("color:#9E9E9E;font-size:11px;border:none;")
    lbl_bookings.setAlignment(Qt.AlignmentFlag.AlignCenter)
    vbox.addWidget(lbl_bookings)

    return card
