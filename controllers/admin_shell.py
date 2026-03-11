"""AdminShellController — cua so admin duy nhat, chua 5 page trong QStackedWidget."""

from widgets.base_window import BaseWindow
from controllers.overview_admin import OverviewAdminPage
from controllers.booking_overview import BookingOverviewPage
from controllers.edit_room import EditRoomPage
from controllers.users_management import UsersManagementPage
from controllers.device_management import DeviceManagementPage


class AdminShellController(BaseWindow):
    PAGE_OVERVIEW = 0
    PAGE_BOOKINGS = 1
    PAGE_ROOMS = 2
    PAGE_USERS = 3
    PAGE_DEVICES = 4

    def __init__(self, user):
        super().__init__(
            user,
            role_text="Admin",
            show_search=True,
            show_sidebar=True,
            title="SmartLocker UEL - Admin",
            use_stack=True,
        )

        # Tao 5 page
        self._overview_page = OverviewAdminPage(self)
        self._bookings_page = BookingOverviewPage(self)
        self._rooms_page = EditRoomPage(self)
        self._users_page = UsersManagementPage(self)
        self._devices_page = DeviceManagementPage(self)

        # Dang ky vao stack
        self.add_page(self._overview_page, "pushButtonOverview")
        self.add_page(self._bookings_page, "pushButtonBookings")
        self.add_page(self._rooms_page, "pushButtonEdit")
        self.add_page(self._users_page, "pushButtonUsers")
        self.add_page(self._devices_page, "pushButtonDevices")

        # Connect sidebar
        self.sidebar.pushButtonOverview.clicked.connect(
            lambda: self._activate_page(self.PAGE_OVERVIEW)
        )
        self.sidebar.pushButtonBookings.clicked.connect(
            lambda: self._activate_page(self.PAGE_BOOKINGS)
        )
        self.sidebar.pushButtonEdit.clicked.connect(
            lambda: self._activate_page(self.PAGE_ROOMS)
        )
        self.sidebar.pushButtonUsers.clicked.connect(
            lambda: self._activate_page(self.PAGE_USERS)
        )
        self.sidebar.pushButtonDevices.clicked.connect(
            lambda: self._activate_page(self.PAGE_DEVICES)
        )
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

        # Mac dinh hien Overview
        self.switch_page(self.PAGE_OVERVIEW)

    def _activate_page(self, index):
        """Chuyen page va refresh du lieu cua page do."""
        self.switch_page(index)
        pages = [
            self._overview_page,
            self._bookings_page,
            self._rooms_page,
            self._users_page,
            self._devices_page,
        ]
        page = pages[index]
        if hasattr(page, "refresh"):
            page.refresh()

    def go_to_rooms(self, preselect_room=None):
        """Chuyen sang tab Rooms, co the preselect 1 room."""
        self.switch_page(self.PAGE_ROOMS)
        if preselect_room:
            self._rooms_page._preselect(preselect_room)
