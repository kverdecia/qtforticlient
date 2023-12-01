from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
)

import qtforticlient.resources


class FortiClientTray(QSystemTrayIcon):
    open_application_clicked = Signal()
    quit_application_clicked = Signal()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._setup_icons()
        self._setup_actions()
        self._setup_menu()

    def _setup_icons(self) -> None:
        self.vpn_default_status_icon = QIcon(':/icons/vpn-default-status.svg')
        self.vpn_error_status_icon = QIcon(':/icons/vpn-error-status.svg')
        self.vpn_connected_status_icon = QIcon(':/icons/vpn-connected-status.svg')
        self.setIcon(self.vpn_default_status_icon)

    def _setup_actions(self) -> None:
        self.open_action = QAction()
        self.open_action.setText("Open QtFortiClient")
        self.open_action.triggered.connect(self.open_application_clicked.emit)

        self.quit_action = QAction()
        self.quit_action.setText("Quit")
        self.quit_action.triggered.connect(self.quit_application_clicked.emit)

    def _setup_menu(self) -> None:
        tray_menu = QMenu()
        tray_menu.addAction(self.open_action)
        tray_menu.addSeparator()
        tray_menu.addAction(self.quit_action)
        self.setContextMenu(tray_menu)

    def show_connection_staring(self) -> None:
        self.setIcon(self.vpn_default_status_icon)
        self.setToolTip("Starting connection to VPN")

    def show_connection_canceled(self) -> None:
        self.setIcon(self.vpn_default_status_icon)
        self.setToolTip("Canceled connection to VPN")

    def show_connection_connecting(self) -> None:
        self.setIcon(self.vpn_default_status_icon)
        self.setToolTip("Connecting to VPN")

    def show_connection_failed(self) -> None:
        self.setIcon(self.vpn_error_status_icon)
        self.setToolTip("Failed to connect to VPN")

    def show_connection_connected(self) -> None:
        self.setIcon(self.vpn_connected_status_icon)
        self.setToolTip("Connected to VPN")

    def show_connection_disconnected(self) -> None:
        self.setIcon(self.vpn_default_status_icon)
        self.setToolTip("Disconnected from VPN")
