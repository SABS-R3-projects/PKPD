import sys

from PyQt5 import QtCore, QtWidgets

from PKPD.gui.abstractGui import AbstractMainWindow

class MainWindow(AbstractMainWindow):
    """MainWindow class which sets up the general geometry and layout of the GUI.
    """
    def __init__(self, app):
        """Initialises the main window.
        """
        super().__init__()

        # set window size.
        self.width_coverage = 0.75 # subjective aesthetical choice
        self.aspect_ratio = 5 / 4 # subjective aesthetical choice
        self.available_geometry = app.desktop().availableGeometry()
        _, _, self.desktop_width, self.desktop_height = self.available_geometry.getRect()

        self.size = self.size()

        self._set_window_size()


    def _set_window_size(self):
        """Keeps an aspect ratio width / height of 5/4 and scales the width such that 0.75 of the screen width is covered. If this
        leads to window height exceeding the scrren height, the aspect ratio is kept and the window height is set to the screen
        height.
        """
        if (self.desktop_width < 1) or (self.desktop_height < 1):
            raise ValueError('Resolution of desktop appears to be too low, i.e. less than a pixel for either width or height.')

        self.width = int(self.desktop_width * self.width_coverage)
        self.height = int(self.width / self.aspect_ratio)

        if self.height > self.desktop_height:
            self.height = self.desktop_height
            self.width = int(self.height * self.aspect_ratio)

        self.size.setWidth(self.width)
        self.size.setHeight(self.height)

        self.setGeometry(QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            self.size,
            self.available_geometry
            )
        )



if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())