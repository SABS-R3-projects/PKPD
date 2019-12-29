from PyQt5 import QtCore, QtWidgets, QtGui

from PKPD.gui import abstractGui, mainWindow

class HomeTab(abstractGui.AbstractHomeTab):
    """HomeTab class responsible for model and data management.
    """
    def __init__(self, main_window:mainWindow.MainWindow):
        """Initialises the home tab.
        """
        super().__init__()
        self.name = 'Model/Data'
        self.main_window = main_window

        # arrange content
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self._create_model_group(), 0, 0)
        grid.addWidget(self._create_data_group(), 1, 0)
        grid.addLayout(self._create_next_button(), 2, 0)

        self.setLayout(grid)


    def _create_model_group(self):
        """Creates the model file dialog group consisting of a label, a button that opens the file dialog, a text field that displays
        the selected file and a check mark symbol that gives feedback whether or not the chosen file is valid.

        Returns:
            {QGroupBox} -- Returns model group object.
        """
        group = QtWidgets.QGroupBox('Model/Protocol:')
        # generate file dialog
        button = QtWidgets.QPushButton('select model file')
        button.clicked.connect(self.on_model_click)
        self.model_text = QtWidgets.QLineEdit('no file selected')
        self.model_check_mark = self._create_file_check_mark()
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


    def _create_data_group(self):
        """Creates the data file dialog group consisting of a label, a button that opens the file dialog, a text field that displays
        the selected file and a check mark symbol that gives feedback whether or not the chosen file is valid.

        Returns:
            {QGroupBox} -- Returns data group object.
        """
        group = QtWidgets.QGroupBox('Data:')
        # generate file dialog
        button = QtWidgets.QPushButton('select data file')
        button.clicked.connect(self.on_data_click)
        self.data_text = QtWidgets.QLineEdit('no file selected')
        self.data_check_mark = self._create_file_check_mark()
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


    def _create_next_button(self):
        """Creates a button to be able to switch to the simulation tab.

        Returns:
            {QPushButton} -- Returns next button.
        """
        button = QtWidgets.QPushButton('next')
        button.clicked.connect(self.on_next_click)
        # arrange button and text horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(button)

        return hbox


    def _create_file_check_mark(self):
        """Creates a label object that indicates whether a chosen data file is valid. Default is a question mark. Upon file
        selection the question mark is replaced by either a green check mark or a red cross.

        Returns:
            {QLabel} -- Returns a check mark label.
        """
        label = QtWidgets.QLabel(self)
        label.setPixmap(self.main_window.rescaled_qm)

        return label


    @QtCore.pyqtSlot()
    def on_model_click(self):
        """Opens a file dialog upon pressing the 'select model/protocol file' and updates after selection the displayed path
        directory and the check mark. Only .mmt files can be selected.
        """
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Model Files (*.mmt)", options=options)
        if fileName:
            # update QLineEdit in the GUI to selected file
            self.model_text.setText(fileName)
            # update check mark
            self.model_check_mark.setPixmap(self.main_window.rescaled_cm)


    @QtCore.pyqtSlot()
    def on_data_click(self):
        """Opens a file dialog upon pressing the 'select data file' and updates after selection the displayed path
        directory and the check mark. Only .csv files can be selected.
        """
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Data Files (*.csv)", options=options)
        if fileName:
            # update QLineEdit in the GUI to selected file
            self.data_text.setText(fileName)
            # update check mark
            self.data_check_mark.setPixmap(self.main_window.rescaled_cm)


    @QtCore.pyqtSlot()
    def on_next_click(self):
        """Executes the MainWindow.next_tab method.
        """
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