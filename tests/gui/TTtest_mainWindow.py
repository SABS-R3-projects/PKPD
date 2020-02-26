import sys

import pytest
import unittest

from PyQt5 import QtWidgets, QtCore

from PKPD.gui.mainWindow import MainWindow


class TestMainWindow(unittest.TestCase):
    """Tests the methods of the MainWindow class.
    """
    def test_set_window_size_square_screen(self, desktop_dimension=[200, 200]):
        """Tests whether the resulting main window size obeys the aspect ratio 5/4 and whether either the width is 3/4 of the sreen
        width or the height is equal the screen height assuming a square desktop 200x200

        Arguments:
            desktop_width {int} -- Screen width in pixel.
        """
        expected_aspect_ratio = 5 / 4
        expected_width_coverage = 3 / 4
        expected_height_coverage = 1

        # assumes square desktop
        desktop_width, desktop_height = desktop_dimension

        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow(app)

        window.desktop_width = desktop_width
        window.desktop_height = desktop_height

        window._set_window_size()

        assert pytest.approx(window.width / window.height, rel=0.05) == expected_aspect_ratio
        assert (pytest.approx(window.width, rel=0.05) == int(desktop_width * expected_width_coverage) or
                pytest.approx(window.height, rel=0.05) == int(desktop_height * expected_height_coverage)
               )

        # closing application, the usual sys.exit(app.exec_()) kept did not close the app automatically.
        QtCore.QTimer.singleShot(0.1, window.close)

    def test_set_window_size_broad_screen(self, desktop_dimension=[1000, 200]):
        """Tests whether the resulting main window size obeys the aspect ratio 5/4 and whether either the width is 3/4 of the sreen
        width or the height is equal the screen height.

        Arguments:
            desktop_dimension {List} -- Screen dimension in pixel.
        """
        expected_aspect_ratio = 5 / 4
        expected_width_coverage = 3 / 4
        expected_height_coverage = 1

        desktop_width, desktop_height = desktop_dimension

        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow(app)

        window.desktop_width = desktop_width
        window.desktop_height = desktop_height

        window._set_window_size()

        assert pytest.approx(window.width / window.height, rel=0.05) == expected_aspect_ratio
        assert (pytest.approx(window.width, rel=0.05) == int(desktop_width * expected_width_coverage) or
                pytest.approx(window.height, rel=0.05) == int(desktop_height * expected_height_coverage)
               )

        # closing application, the usual sys.exit(app.exec_()) kept did not close the app automatically.
        QtCore.QTimer.singleShot(0.1, window.close)

    def test_set_window_size_high_screen(self, desktop_dimension=[200, 1000]):
        """Tests whether the resulting main window size obeys the aspect ratio 5/4 and whether either the width is 3/4 of the sreen
        width or the height is equal the screen height.

        Arguments:
            desktop_dimension {List} -- Screen dimension in pixel.
        """
        expected_aspect_ratio = 5 / 4
        expected_width_coverage = 3 / 4
        expected_height_coverage = 1

        desktop_width, desktop_height = desktop_dimension

        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow(app)

        window.desktop_width = desktop_width
        window.desktop_height = desktop_height

        window._set_window_size()

        assert pytest.approx(window.width / window.height, rel=0.05) == expected_aspect_ratio
        assert (pytest.approx(window.width, rel=0.05) == int(desktop_width * expected_width_coverage) or
                pytest.approx(window.height, rel=0.05) == int(desktop_height * expected_height_coverage)
               )

        # closing application, the usual sys.exit(app.exec_()) kept did not close the app automatically.
        QtCore.QTimer.singleShot(0.1, window.close)