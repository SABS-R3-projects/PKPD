import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QStyle

from abstractGui import AbstractMainWindow

class MainWindow(AbstractMainWindow):
    def __init__(self):
        super().__init__()

        self.width_coverage = 0.75
        self.aspect_ratio = 5 / 4
        self.available_geometry = app.desktop().availableGeometry()

        self.size = self.size()

        self._set_window_size()


    def _set_window_size(self):
        _, _, desktop_width, desktop_height = self.available_geometry.getRect()

        if (desktop_width < 1) or (desktop_height < 1):
            raise ValueError('Resolution of desktop is too low, i.e. less than a pixel for either width or height.')

        self.width = int(desktop_width * self.width_coverage)
        self.height = int(self.width / self.aspect_ratio)

        if self.height > desktop_height:
            self.height = desktop_height
            self.width = int(self.height * self.aspect_ratio)

        self.size.setWidth(self.width)
        self.size.setHeight(self.height)

        self.setGeometry(QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            self.size,
            self.available_geometry
            )
        )

        self.show()



if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())