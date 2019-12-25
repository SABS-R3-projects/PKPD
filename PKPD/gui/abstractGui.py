from PyQt5 import QtWidgets

class AbstractMainWindow(QtWidgets.QMainWindow):

    def _set_window_size(self):
        # set the default window size (make sure not fixed)
        raise NotImplementedError

