import os

from PyQt5 import QtCore, QtWidgets, QtGui

from PKPD.gui import abstractGui, mainWindow

class HomeTab(abstractGui.AbstractHomeTab):
    """HomeTab class responsible for model and data management.
    """
    def __init__(self, main_window):
        """Initialises the home tab.
        """
        super().__init__()
        self.name = 'Model/Data'
        self.main_window = main_window
        self.is_model_file_valid = False
        self.is_data_file_valid = False

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
        group = QtWidgets.QGroupBox('Model:')

        # create file dialog button and text field
        file_dialog = self._create_file_dialog()

        # create display of mmt file
        model_diplay = self._create_model_display()

        # arrange button/text and label vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(file_dialog)
        vbox.addLayout(model_diplay)
        vbox.addStretch(1)

        group.setLayout(vbox)

        return group


    def _create_file_dialog(self):
        # generate file dialog
        button = QtWidgets.QPushButton('select model file')
        button.clicked.connect(self.on_model_click)

        # display path to model file
        self.model_path_text_field = QtWidgets.QLineEdit('no file selected')

        # make text field non-editable
        self.model_path_text_field.setReadOnly(True)

        # create file check mark
        self.model_check_mark = self._create_file_check_mark()

        # arrange button and text horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(button)
        hbox.addWidget(self.model_path_text_field)
        hbox.addWidget(self.model_check_mark)

        return hbox


    def _create_model_display(self):
        # create text field to display model
        self.model_display_text_field = QtWidgets.QTextEdit()

        # adjust color of text field
        self.model_display_text_field.setStyleSheet("background-color: rgb(128,128,128);")

        # make text field non-editable
        self.model_display_text_field.setReadOnly(True)

        # make display scrollable, such that window is never exceeded
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.model_display_text_field)
        scroll.setWidgetResizable(True)

        # fix vertical space that display can take up
        height = 0.35 * self.main_window.height
        scroll.setFixedHeight(height)

        # fix horizontal space that display can take up
        width = 0.9 * self.main_window.width
        scroll.setFixedWidth(width)

        # arrange display window horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(2)
        hbox.addWidget(scroll)
        hbox.addStretch(1)

        return hbox


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
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Model Files (*.mmt)", options=options)

        if file_path:
            # check format of file
            self.is_model_file_valid = self._is_model_file_valid(file_path)

            if self.is_model_file_valid:
                # update QLineEdit in the GUI to selected file
                self.model_path_text_field.setText(file_path)

                # update check mark
                self.model_check_mark.setPixmap(self.main_window.rescaled_cm)

                # update model display
                with open(file_path, 'r') as model_file:
                    contents = model_file.read()
                    self.model_display_text_field.setText(contents)
            else:
                # update QLineEdit in the GUI
                self.model_path_text_field.setText('The selected file is invalid!')

                # update check mark
                self.model_check_mark.setPixmap(self.main_window.rescaled_rc)


    def _is_model_file_valid(self, file_path:str):
        # check existence
        is_file_existent = os.path.isfile(file_path)

        # check format
        is_format_correct = file_path.split('.')[-1] == 'mmt'

        # are both citeria satisifed
        is_path_valid = is_file_existent and is_format_correct

        return is_path_valid


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