import sys

import pytest
import unittest
from hypothesis import given, strategies

from PyQt5 import QtWidgets, QtCore

from PKPD.gui.mainWindow import MainWindow

class TestMainWindow(unittest.TestCase):
    """Tests the methods of the MainWindow class.
    """
    @given(desktop_dimension=strategies.lists(strategies.integers(min_value=200), min_size=2, max_size=2))
    def test_set_window_size(self, desktop_dimension):
        """Tests whether the resulting main window size obeys the aspect ratio 5/4 and whether either the width is 3/4 of the sreen
        width or the height is equal the screen height.

        Arguments:
            desktop_width {int} -- Screen width in pixel.
        """
        desktop_width, desktop_height= desktop_dimension

        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow(app)

        window.desktop_width = desktop_width
        window.desktop_height = desktop_height

        window._set_window_size()

        assert pytest.approx(window.width / window.height, rel=0.05) == window.aspect_ratio
        assert (pytest.approx(window.width, rel=0.05) == int(desktop_width * 0.75) or
                pytest.approx(window.height, rel=0.05) == int(desktop_height)
               )


        # closing application, the usual sys.exit(app.exec_()) kept did not close the app automatically.
        QtCore.QTimer.singleShot(0.1, window.close)

    # @given(desktop_width=strategies.integers(min_value=200, max_value=10000))
    # def test_set_window_size_width(self, desktop_width):
    #     """Tests whether the resulting main window size obeys the aspect ratio 5/4 and whether either the width is 3/4 of the sreen
    #     width or the height is equal the screen height.

    #     Arguments:
    #         desktop_width {int} -- Screen width in pixel.
    #     """
    #     desktop_height= 1080 # arbitrary value

    #     app = QtWidgets.QApplication(sys.argv)
    #     window = MainWindow(app)

    #     window.desktop_width = desktop_width
    #     window.desktop_height = desktop_height

    #     window._set_window_size()

    #     assert pytest.approx(window.width / window.height, rel=0.05) == window.aspect_ratio
    #     assert (pytest.approx(window.width, rel=0.05) == int(desktop_width * 0.75) or
    #             pytest.approx(window.height, rel=0.05) == int(desktop_height)
    #            )


    #     # closing application, the usual sys.exit(app.exec_()) kept did not close the app automatically.
    #     QtCore.QTimer.singleShot(0.1, window.close)


    # @given(desktop_height=strategies.integers(min_value=200, max_value=10000))
    # def test_set_window_size_height(self, desktop_height):
    #     """Tests whether the resulting main window size obeys the aspect ratio 5/4 and whether either the width is 3/4 of the sreen
    #     width or the height is equal the screen height.

    #     Arguments:
    #         desktop_width {int} -- Screen width in pixel.
    #     """
    #     desktop_width= 1080 # arbitrary value

    #     app = QtWidgets.QApplication(sys.argv)
    #     window = MainWindow(app)

    #     window.desktop_width = desktop_width
    #     window.desktop_height = desktop_height

    #     window._set_window_size()

    #     assert pytest.approx(window.width / window.height, rel=0.05) == window.aspect_ratio
    #     assert (pytest.approx(window.width, rel=0.05) == int(desktop_width * 0.75) or
    #             pytest.approx(window.height, rel=0.05) == int(desktop_height)
    #            )


    #     # closing application, the usual sys.exit(app.exec_()) kept did not close the app automatically.
    #     QtCore.QTimer.singleShot(0.1, window.close)