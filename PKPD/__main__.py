import sys
import PKPD.gui.mainWindow as mainwindow
from PyQt5 import QtWidgets


def main():
    # Create window instance
    app = QtWidgets.QApplication(sys.argv)
    window = mainwindow.MainWindow(app)

    # show window
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
