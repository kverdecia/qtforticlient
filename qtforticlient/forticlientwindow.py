import logging

from rich.logging import RichHandler

from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QWidget,
    QMessageBox,
)

import qtforticlient.resources
from .forticlientconnection import VPNConnection


logging.basicConfig(level=logging.INFO, handlers=[RichHandler(omit_repeated_times=False)])


class FortiClientWindow(QMainWindow):
    vpn_connection: VPNConnection | None
    application: QApplication

    vpn_connection_started = Signal()
    vpn_connection_canceled = Signal()
    vpn_connection_connecting = Signal()
    vpn_connection_failed = Signal()
    vpn_connection_connected = Signal()
    vpn_connection_disconnected = Signal()

    def __init__(self, application: QApplication):
        super().__init__()
        self.application = application


        self.setWindowTitle("QtFortiClient")
        self.setFixedWidth(350)

        self._setup_icons()
        self._setup_actions()
        self._setup_main_content()

        self.threadpool = QThreadPool()
        self.vpn_connection = None

    def _setup_icons(self) -> None:
        self.connect_icon = QIcon(':/icons/connect.png')
        self.disconnect_icon = QIcon(':/icons/disconnect.png')
        self.bars_icon = QIcon(':/icons/bars.svg')
        self.vpn_connected_icon = QIcon(':/icons/vpn-connected.svg')
        self.vpn_disconnected_icon = QIcon(':/icons/vpn-disconnected.svg')

    def _setup_actions(self) -> None:
        self.connect_action = QAction(self)
        self.connect_action.setIcon(self.connect_icon)
        self.connect_action.setText("Connect")
        self.connect_action.setStatusTip("Connect to VPN")
        self.connect_action.setToolTip("Connect to VPN")
        self.connect_action.setEnabled(False)
        self.connect_action.setCheckable(True)
        self.connect_action.triggered.connect(self.on_connect_to_vpn)

        self.starting_action = QAction()
        self.starting_action.setIcon(self.connect_icon)
        self.starting_action.setText("Starting...")
        self.starting_action.setStatusTip("Starting connection to VPN")
        self.starting_action.setToolTip("Starting connection to VPN")
        self.starting_action.setEnabled(False)

        self.canceled_action = QAction()
        self.canceled_action.setIcon(self.connect_icon)
        self.canceled_action.setText("&Connect to VPN")
        self.canceled_action.setEnabled(True)

        self.connecting_action = QAction()
        self.connecting_action.setIcon(self.connect_icon)
        self.connecting_action.setText("Connecting...")
        self.connecting_action.setStatusTip("Connecting to VPN")
        self.connecting_action.setToolTip("Connecting to VPN")
        self.connecting_action.setEnabled(False)

        self.failed_action = QAction()
        self.failed_action.setIcon(self.connect_icon)
        self.failed_action.setText("&Connect to VPN")
        self.failed_action.setEnabled(True)

        self.connected_action = QAction()
        self.connected_action.setIcon(self.disconnect_icon)
        self.connected_action.setText("&Disconnect from VPN")
        self.connected_action.setEnabled(True)

        self.disconnected_action = QAction()
        self.disconnected_action.setIcon(self.connect_icon)
        self.disconnected_action.setText("&Connect to VPN")
        self.disconnected_action.setEnabled(True)

    def _setup_main_content(self) -> None:
        form_layout = QFormLayout()
        self.window_layout = QVBoxLayout()
        self.window_layout.addLayout(form_layout)

        self.server_edit = QLineEdit()
        self.server_edit.textChanged.connect(self.validate_params)
        form_layout.addRow('Server:', self.server_edit)

        self.username_edit = QLineEdit()
        self.username_edit.textChanged.connect(self.validate_params)
        form_layout.addRow('Username:', self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)  # type: ignore
        self.password_edit.textChanged.connect(self.validate_params)
        form_layout.addRow('Password:', self.password_edit)

        buttons_layout = QHBoxLayout()
        self.window_layout.addLayout(buttons_layout)
        self.connection_button = QPushButton('&Connect to VPN')
        self.connection_button.clicked.connect(self.on_connect_to_vpn)
        self.connection_button.setIcon(self.connect_icon)
        self.connection_button.setEnabled(False)
        buttons_layout.addWidget(self.connection_button, stretch=0, alignment=Qt.AlignRight)  # type: ignore

        widget = QWidget()
        widget.setLayout(self.window_layout)
        self.setCentralWidget(widget)

    def create_vpn_connection(self) -> VPNConnection:
        server = self.get_server()
        username = self.get_username()
        password = self.get_password()
        vpn_connection = VPNConnection(server, username, password)
        vpn_connection.signals.starting_vpn.connect(self.on_starting_vpn)
        vpn_connection.signals.canceled_vpn.connect(self.on_canceled_vpn)
        vpn_connection.signals.connecting_vpn.connect(self.on_connecting_vpn)
        vpn_connection.signals.failed_vpn.connect(self.on_failed_vpn)
        vpn_connection.signals.connected_vpn.connect(self.on_connected_vpn)
        vpn_connection.signals.disconnected_vpn.connect(self.on_disconnected_vpn)
        return vpn_connection

    def get_server(self) -> str:
        return self.server_edit.text()
    
    def get_username(self) -> str:
        return self.username_edit.text()
    
    def get_password(self) -> str:
        return self.password_edit.text()
    
    def validate_params(self, *args) -> None:
        isEnabled = bool(self.get_server().strip() and self.get_username().strip() and self.get_password().strip())
        # self.connect_action.setEnabled(isEnabled)
        self.connection_button.setEnabled(isEnabled)

    def setFieldsEnabled(self, isEnabled: bool) -> None:
        self.server_edit.setEnabled(isEnabled)
        self.username_edit.setEnabled(isEnabled)
        self.password_edit.setEnabled(isEnabled)

    def on_connect_to_vpn(self):
        if self.vpn_connection is None:
            self.vpn_connection = self.create_vpn_connection()
            self.setFieldsEnabled(False)
            self.connection_button.setEnabled(False)
            self.threadpool.start(self.vpn_connection)
        elif self.vpn_connection.is_connected:
            self.setFieldsEnabled(False)
            self.connection_button.setEnabled(False)
            self.threadpool.start(self.vpn_connection.disconnect)

    def update_connection_button(self, action: QAction) -> None:
        self.connection_button.setEnabled(action.isEnabled())
        self.connection_button.setIcon(action.icon())
        self.connection_button.setText(action.text())
        self.connection_button.setToolTip(action.toolTip())
        self.connection_button.setStatusTip(action.statusTip())

    def on_starting_vpn(self):
        self.setFieldsEnabled(False)
        self.update_connection_button(self.starting_action)
        self.vpn_connection_started.emit()

    def on_canceled_vpn(self):
        self.setFieldsEnabled(True)
        self.update_connection_button(self.canceled_action)
        self.vpn_connection_canceled.emit()
        QMessageBox.warning(self, 'Warning', 'Canceled the connection to the vpn')

    def on_connecting_vpn(self):
        self.setFieldsEnabled(False)
        self.update_connection_button(self.connecting_action)
        self.vpn_connection_connecting.emit()

    def on_failed_vpn(self):
        self.setFieldsEnabled(True)
        self.update_connection_button(self.failed_action)
        self.vpn_connection_failed.emit()
        QMessageBox.critical(self, 'Error', 'Failed to connect to VPN')

    def on_connected_vpn(self):
        self.setFieldsEnabled(False)
        self.update_connection_button(self.connected_action)
        self.vpn_connection_connected.emit()
        QMessageBox.information(self, 'Success', 'You are now connected to VPN')

    def on_disconnected_vpn(self):
        self.setFieldsEnabled(True)
        self.update_connection_button(self.disconnected_action)
        self.vpn_connection_disconnected.emit()
        QMessageBox.information(self, 'Success', 'You are now disconnected from VPN')
