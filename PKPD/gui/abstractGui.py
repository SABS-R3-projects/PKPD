from PyQt5 import QtWidgets


class AbstractMainWindow(QtWidgets.QMainWindow):
    def _set_window_size(self):
        # set the default window size (make sure not fixed)
        raise NotImplementedError

    def _arrange_window_content(self):
        # arranges the content of main window
        raise NotImplementedError

    def _create_tabs(self):
        # creates tabs e.g. for model/data management and simulation
        raise NotImplementedError

    def _create_status_bar(self):
        # creates status bar
        raise NotImplementedError

    def next_tab(self):
        # moves to the next tab.
        raise NotImplementedError


class AbstractHomeTab(QtWidgets.QWidget):
    def _create_model_group(self):
        # creates group object arranging the model file dialog.
        raise NotImplementedError

    def _create_data_group(self):
        # creates group object arranging the data file dialog.
        raise NotImplementedError

    def _create_next_button(self):
        # creates button that allows to switch to the next tab.
        raise NotImplementedError
