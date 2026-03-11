"""AdminShellController -- the single admin window containing 5 pages in a QStackedWidget."""

from widgets.base_window import BaseWindow
from controllers.overview_admin import OverviewAdminPage
from controllers.booking_overview import BookingOverviewPage
from controllers.edit_room import EditRoomPage
from controllers.users_management import UsersManagementPage
from controllers.device_management import DeviceManagementPage


class AdminShellController(BaseWindow):
    """Main admin window that hosts all management pages in a QStackedWidget.

    Provides navigation between Overview, Bookings, Rooms, Users, and Devices
    pages via the sidebar. Each page is refreshed upon activation.

    Args:
        user (dict): The authenticated admin user record.
    """

    PAGE_OVERVIEW = 0
    PAGE_BOOKINGS = 1
    PAGE_ROOMS = 2
    PAGE_USERS = 3
    PAGE_DEVICES = 4

    def __init__(self, user):
        """Initialize the admin shell with all management pages and sidebar navigation."""
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
        """Switch to the page at the given index and refresh its data.

        Args:
            index (int): The zero-based page index corresponding to one of
                the PAGE_* class constants.
        """
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
        """Navigate to the Rooms management page, optionally pre-selecting a room.

        Args:
            preselect_room (dict or None): An optional room dictionary to
                highlight in the rooms table after switching. Defaults to None.
        """
        self.switch_page(self.PAGE_ROOMS)
        if preselect_room:
            self._rooms_page._preselect(preselect_room)
