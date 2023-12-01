import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
)

import qtforticlient.resources
from qtforticlient.forticlienttray import FortiClientTray
from qtforticlient.forticlientwindow import FortiClientWindow

try:
    from ctypes import windll  # type: ignore
    myappid = "kavosoft.internaltools.qtforticlient.version"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    ...


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/appicon.svg"))
    app.setQuitOnLastWindowClosed(False)
    window = FortiClientWindow(app)
    tray = FortiClientTray(app)
    tray.open_application_clicked.connect(window.show)
    tray.quit_application_clicked.connect(app.quit)
    window.vpn_connection_started.connect(tray.show_connection_staring)
    window.vpn_connection_canceled.connect(tray.show_connection_canceled)
    window.vpn_connection_connecting.connect(tray.show_connection_connecting)
    window.vpn_connection_failed.connect(tray.show_connection_failed)
    window.vpn_connection_connected.connect(tray.show_connection_connected)
    window.vpn_connection_disconnected.connect(tray.show_connection_disconnected)
    tray.show()

    app.exec()


if __name__ == "__main__":
    main()
