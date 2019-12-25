import sys

from PyQt5 import QtCore, QtWidgets

from PKPD.gui import abstractGui, home #import AbstractMainWindow

class MainWindow(abstractGui.AbstractMainWindow):
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

        # set geometry of window.
        self.top_bar = QtWidgets.QMenuBar()
        self.tab_view = None
        self.bottom_bar = QtWidgets.QStatusBar()


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


    def _set_geometry(self):
        """Method which sets the layout of the main window"""
        self._set_tab_structure()
        self.setMenuBar(self.top_bar)
        self.setCentralWidget(self.tab_view)
        self.setStatusBar(self.bottom_bar)
        # we can add more stuff here once the Program gets more complicated


    def _set_tab_structure(self):
        """Method which sets the structure of tabs within the window"""
        self.tab_view = QtWidgets.QTabWidget()
        for tab in self.tabs:
            self.tab_view.addTab(tab, tab.name)


if __name__ == '__main__':

    # Create window instance
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)

    # add some content
    window.top_bar.addMenu('File')
    tab1, tab2 = home.TestTab("Model"), home.TestTab("Simulation")
    window.tabs = [tab1, tab2]
    version_number = QtWidgets.QLabel('Version: 0.0.0')
    window.bottom_bar.addWidget(version_number)
    window._set_geometry()
    window.setWindowTitle('PKPD')

    # show window
    window.show()
    sys.exit(app.exec_())