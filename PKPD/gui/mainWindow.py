import os
import sys

from PyQt5 import QtCore, QtWidgets, QtGui

from PKPD.gui import abstractGui

class MainWindow(abstractGui.AbstractMainWindow):
    """MainWindow class which sets up the general geometry and layout of the GUI.
    """
    def __init__(self, app):
        """Initialises the main window.
        """
        super().__init__()
        self.window_title = 'Pharmacokinetics/Pharamcodynamics'
        self.version_number = QtWidgets.QLabel('Version: 0.0.0')
        self.producers = QtWidgets.QLabel('SABS R3')
        # variables needed across tabs
        self.model_file = None
        self.data_file = None
        # set window size.
        self.width_coverage = 0.75 # subjective aesthetical choice
        self.aspect_ratio = 5 / 4 # subjective aesthetical choice
        self.available_geometry = app.desktop().availableGeometry()
        _, _, self.desktop_width, self.desktop_height = self.available_geometry.getRect()
        self.size = self.size()
        self._set_window_size()
        # check marks for file dialog
        question_mark = QtGui.QPixmap('QUESTION.png')
        self.rescaled_qm = question_mark.scaledToHeight(self.desktop_height * 0.025)
        check_mark = QtGui.QPixmap('CHECK.png')
        self.rescaled_cm = check_mark.scaledToHeight(self.desktop_height * 0.025)
        red_cross = QtGui.QPixmap('FALSE.png')
        self.rescaled_rc = red_cross.scaledToHeight(self.desktop_height * 0.03)
        # fill the empty window with content
        self._arrange_window_content()


    def _set_window_size(self):
        """Keeps an aspect ratio width / height of 5/4 and scales the width such that 0.75 of the screen width is covered. If this
        leads to a window height exceeding the screen height, the aspect ratio is kept and the window height is set to the screen
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


    def _arrange_window_content(self):
        """Defines the layout of the main window.
        """
        self.setWindowTitle(self.window_title)
        self.tabs = self._create_tabs()
        self.setCentralWidget(self.tabs)
        self.setStatusBar(self._create_status_bar())


    def _create_tabs(self):
        """Creates the home and simulation tab.

        Returns:
            {QTabWidget} -- A TabWidget containing the home and simulation tab.
        """
        # generate tabs.
        self.home = HomeTab(self)
        simulation = TestTab("Simulation")
        # add tabs to tab widget.
        tabs = QtWidgets.QTabWidget()
        self.home_tab_index = tabs.addTab(self.home, self.home.name)
        self.sim_tab_index = tabs.addTab(simulation, simulation.name)

        return tabs


    def _create_status_bar(self):
        """Creates a status bar displaying the current program version and the producers of the program.

        Returns:
            {QStatusBar} -- A StatusbarWidget with the version number and the producers.
        """
        status_bar = QtWidgets.QStatusBar()
        status_bar.addWidget(self._create_SABS_logo())
        status_bar.addWidget(self.producers)
        status_bar.addWidget(self.version_number)

        return status_bar


    def _create_SABS_logo(self):
        label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap('SABSR3.png')
        rescaled_pixmap = pixmap.scaledToHeight(self.desktop_height * 0.03)
        label.setPixmap(rescaled_pixmap)

        return label


    def next_tab(self):
        """Switches to the simulation tab, when triggered by pressing a QPushButton on the home tab.
        """
        ### SANITY CHECK: both files exist and have the correct file format.
        model_file = self.home.model_text.text()
        data_file = self.home.data_text.text()
        if os.path.isfile(model_file) and os.path.isfile(data_file):
            # save files to make them accessible to simulation
            self.model_file = model_file
            self.data_file = data_file
            # switch to simulation tab
            self.tabs.setCurrentIndex(self.sim_tab_index)
        else:
            # generate error message
            error_message = 'At least one of the files does not seem to exist. Please check again!'
            QtWidgets.QMessageBox.question(self, 'Files not found!', error_message, QtWidgets.QMessageBox.Yes)
            # TODO:
            # check above whether file format is ok and then set wrong file to cross





###########################################################
# TODO: seperate into home.py
class HomeTab(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.name = 'Model/Data'
        self.main_window = main_window

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.create_model_group(), 0, 0)
        grid.addWidget(self.create_data_group(), 1, 0)
        grid.addLayout(self.create_next_button(), 2, 0)

        self.setLayout(grid)


    def create_model_group(self):
        group = QtWidgets.QGroupBox('Model/Protocol:')
        # generate file dialog
        button = QtWidgets.QPushButton('select model file')
        button.clicked.connect(self.on_model_click)
        self.model_text = QtWidgets.QLineEdit('no file selected')
        self.model_check_mark = self._create_question_mark()
        # arrange button and text horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(button)
        hbox.addWidget(self.model_text)
        hbox.addWidget(self.model_check_mark)
        # arrange button/text and label vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        group.setLayout(vbox)

        return group


    def create_data_group(self):
        group = QtWidgets.QGroupBox('Data:')
        # generate file dialog
        button = QtWidgets.QPushButton('select data file')
        button.clicked.connect(self.on_data_click)
        self.data_text = QtWidgets.QLineEdit('no file selected')
        self.data_check_mark = self._create_question_mark()
        # arrange button and text horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(button)
        hbox.addWidget(self.data_text)
        hbox.addWidget(self.data_check_mark)
        # arrange button/text and label vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        group.setLayout(vbox)

        return group


    def create_next_button(self):
        button = QtWidgets.QPushButton('next')
        button.clicked.connect(self.on_next_click)
        # arrange button and text horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(button)

        return hbox


    def _create_question_mark(self):
        label = QtWidgets.QLabel(self)
        label.setPixmap(self.main_window.rescaled_qm)

        return label


    @QtCore.pyqtSlot()
    def on_model_click(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Model Files (*.mmt)", options=options)
        if fileName:
            # update QLineEdit in the GUI to selected file
            self.model_text.setText(fileName)
            # update check mark
            self.model_check_mark.setPixmap(self.main_window.rescaled_cm)


    @QtCore.pyqtSlot()
    def on_data_click(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Data Files (*.csv)", options=options)
        if fileName:
            # update QLineEdit in the GUI to selected file
            self.data_text.setText(fileName)
            # update check mark
            self.data_check_mark.setPixmap(self.main_window.rescaled_cm)


    @QtCore.pyqtSlot()
    def on_next_click(self):
        self.main_window.next_tab()


class TestTab(QtWidgets.QWidget):
    """temporary tab class to test the functionality of tab production in MainWindow"""
    def __init__(self, tab_name):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        text = QtWidgets.QPlainTextEdit()
        layout.addWidget(text)
        self.setLayout(layout)
        self.name = tab_name

##########################################################

if __name__ == '__main__':

    # Create window instance
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)

    # # add some content
    # window.top_bar.addMenu('File')
    # tab1, tab2 = HomeTab(), TestTab("Simulation")
    # window.tabs = [tab1, tab2]
    # version_number = QtWidgets.QLabel('Version: 0.0.0')
    # window.bottom_bar.addWidget(version_number)
    # window._set_geometry()
    # window.setWindowTitle('PKPD')

    # show window
    window.show()
    sys.exit(app.exec_())