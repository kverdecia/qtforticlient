import logging
import signal

import pexpect
from rich.logging import RichHandler

from PySide6.QtCore import QObject, Slot, QRunnable, Signal


logging.basicConfig(level=logging.INFO, handlers=[RichHandler(omit_repeated_times=False)])


class VpnSignals(QObject):
    starting_vpn = Signal()
    canceled_vpn = Signal()
    connecting_vpn = Signal()
    failed_vpn = Signal()
    connected_vpn = Signal()
    disconnected_vpn = Signal()


class VPNConnection(QRunnable):
    server: str
    username: str
    password: str
    child: pexpect.spawn | None
    is_connected: bool

    def __init__(self, server: str, username: str, password: str):
        super().__init__()
        self.server = server
        self.username = username
        self.password = password
        self.child = None
        self.signals = VpnSignals()
        self.is_connected = False

    def _canceled_vpn(self):
        if self.child is None:
            raise Exception('Child process is not running')
        logging.error('Canceled the connection to the vpn')
        self.is_connected = False
        self.signals.canceled_vpn.emit()
        self.child.close()
        self.child = None

    def _connected_vpn(self):
        if self.child is None:
            raise Exception('Child process is not running')
        logging.info('Connected to VPN')
        self.is_connected = True
        self.signals.connected_vpn.emit()

    def _failed_vpn(self):
        if self.child is None:
            raise Exception('Child process is not running')
        logging.error('Failed to connect to VPN')
        self.is_connected = False
        self.signals.failed_vpn.emit()
        self.child.close()
        self.child = None

    def _connecting_vpn(self):
        if self.child is None:
            raise Exception('Child process is not running')
        logging.info('Connecting to VPN')
        self.is_connected = False
        self.signals.connecting_vpn.emit()
        self.child.sendline(self.password)
        result = self.child.expect(['Tunnel is up and running.', pexpect.EOF])
        if result == 0:
            self._connected_vpn()
        elif result == 1:
            self._failed_vpn()

    def _starting_vpn(self):
        logging.info('Starting VPN Connection')
        self.is_connected = False
        self.signals.starting_vpn.emit()
        cmd = f'pkexec openfortivpn {self.server} -u {self.username}'
        self.child = pexpect.spawn(cmd, timeout=None)  # type: ignore
        response = self.child.expect(['VPN account password:', pexpect.EOF])
        if response == 0:
                self._connecting_vpn()
        elif response == 1:
            self._canceled_vpn()

    def _disconnected_vpn(self):
        if self.child is None:
            raise Exception('Child process is not running')
        logging.info('Disconnected from VPN')
        self.is_connected = False
        self.signals.disconnected_vpn.emit()
        self.child.kill(signal.SIGINT)
        self.child.close()
        self.child = None

    @Slot()
    def run(self):
        self._starting_vpn()

    @Slot()
    def disconnect(self):
        self._disconnected_vpn()

    def __del__(self):
        if self.child is not None:
            self.child.close()
        logging.info('VPNConnection object deleted')

