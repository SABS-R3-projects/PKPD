from PyQt5.QtWidgets import QMainWindow

class AbstractMainWindow(QMainWindow):

    def _set_window_size(self):
        # set the default window size (make sure not fixed)
        raise NotImplementedError

