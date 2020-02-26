import sys
import PKPD.gui.mainWindow as mainWindow
from PyQt5 import QtWidgets


def main():
    # Create window instance
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow.MainWindow(app)

    # show window
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
