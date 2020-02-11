import os

import numpy as np
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
        self.library_directory = 'PKPD/modelRepository/'
        self.model_file = None

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

        # create model selection group
        model_selection_group = self._create_model_selection_group()

        # create display of mmt file
        model_display = self._create_model_display()

        # arrange button/text and label vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(model_selection_group)
        vbox.addLayout(model_display)
        vbox.addStretch(1)

        group.setLayout(vbox)

        return group


    def _create_model_selection_group(self):
        # create model selection button
        model_selection_button = QtWidgets.QPushButton('select model')
        model_selection_button.clicked.connect(self.on_select_model_click)

        # create model selection window
        self._create_model_selection_window()

        # display path to model file
        self.model_path_text_field = QtWidgets.QLineEdit('no file selected')

        # make text field non-editable
        self.model_path_text_field.setReadOnly(True)

        # create file check mark
        self.model_check_mark = self._create_file_check_mark()

        # arrange button and text horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(model_selection_button)
        hbox.addWidget(self.model_path_text_field)
        hbox.addWidget(self.model_check_mark)

        return hbox


    def _create_model_selection_window(self):
        # initialise pop-up window
        self.model_selection_window = QtWidgets.QDialog()
        self.model_selection_window.setWindowTitle('Model Selection')

        # define dropdown dimension (otherwise the width will differ as number of char varies)
        self.dropdown_menu_width = 100 # value arbitrary

        # create 'select from library' group
        model_library_group = self._create_model_library_group()

        # create select, cancel, file button group
        button_group = self._create_model_button_group()

        # arange window content vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(model_library_group)
        vbox.addLayout(button_group)

        # add options to window
        self.model_selection_window.setLayout(vbox)


    def _create_model_library_group(self):
        # initialise group
        group = QtWidgets.QGroupBox('Model library:')

        # create number of compartments options
        compartment_options = self._create_compartment_options()

        # create dosing options
        dose_options = self._create_dose_options()

        # create trasition rate options
        transition_rate_options = self._create_transition_rate_options()

        # arange vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(compartment_options)
        vbox.addLayout(dose_options)
        vbox.addLayout(transition_rate_options)
        vbox.addStretch(1)
        group.setLayout(vbox)

        return group


    def _create_compartment_options(self):
        # create label
        label = QtWidgets.QLabel('number of compartments:')

        # define options
        valid_numbers = ['1', '2']

        # create dropdown menu for options
        self.compartment_dropdown_menu = QtWidgets.QComboBox()
        self.compartment_dropdown_menu.setMaximumWidth(self.dropdown_menu_width)
        for number in valid_numbers:
            self.compartment_dropdown_menu.addItem(number)

        # arange label and dropdown menu horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.compartment_dropdown_menu)

        return hbox


    def _create_dose_options(self):
        # create label
        label = QtWidgets.QLabel('dose type:')

        # define options
        valid_types = ['bolus', 'subcut']

        # create dropdown menu for options
        self.dose_type_dropdown_menu = QtWidgets.QComboBox()
        self.dose_type_dropdown_menu.setMaximumWidth(self.dropdown_menu_width)
        for dose_type in valid_types:
            self.dose_type_dropdown_menu.addItem(dose_type)

        # arange label and dropdown menu horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.dose_type_dropdown_menu)

        return hbox


    def _create_transition_rate_options(self):
        # create label
        label = QtWidgets.QLabel('transition rates:')

        # define options
        valid_rates = ['linear']

        # create dropdown menu for options
        self.transition_rate_dropdown_menu = QtWidgets.QComboBox()
        self.transition_rate_dropdown_menu.setMaximumWidth(self.dropdown_menu_width)
        for transition_rate in valid_rates:
            self.transition_rate_dropdown_menu.addItem(transition_rate)

        # arange label and dropdown menu horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.transition_rate_dropdown_menu)

        return hbox


    def _create_model_button_group(self):
        # create 'select from files' button
        select_button = QtWidgets.QPushButton('select model')
        select_button.clicked.connect(self.on_model_select_click)

        # create 'select from files' button
        cancel_button = QtWidgets.QPushButton('cancel')
        cancel_button.clicked.connect(self.on_model_cancel_click)

        # create 'select from files' button
        file_button = QtWidgets.QPushButton('select from file')
        file_button.clicked.connect(self.on_model_file_click)

        # arange buttons horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(select_button)
        hbox.addWidget(cancel_button)
        hbox.addWidget(file_button)

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
    def on_select_model_click(self):
        self.model_selection_window.open()


    @QtCore.pyqtSlot()
    def on_model_select_click(self):
        # mark selected file as valid
        self.is_model_file_valid = True

        # get model descriptives
        descriptives = [
            self.compartment_dropdown_menu.currentText(),
            self.dose_type_dropdown_menu.currentText(),
            self.transition_rate_dropdown_menu.currentText()
        ]

        # reconstruct model file
        self.model_file = self.library_directory + '_'.join(descriptives) + '.mmt'

        # update QLineEdit in the GUI to selected file
        meta_data = [
            'No. Copmartments: ',
            'Dose Type: ',
            'Transition Rates: '
        ]
        text = ''
        for desc_id, descriptive in enumerate(descriptives):
            text = text + meta_data[desc_id] + descriptive + '; '

        self.model_path_text_field.setText(text)

        # update check mark
        self.model_check_mark.setPixmap(self.main_window.rescaled_cm)

        # update model display
        with open(self.model_file, 'r') as model_file:
            contents = model_file.read()
            self.model_display_text_field.setText(contents)

        # close select model window
        self.model_selection_window.close()


    @QtCore.pyqtSlot()
    def on_model_cancel_click(self):
        self.model_selection_window.close()


    @QtCore.pyqtSlot()
    def on_model_file_click(self):
        """Opens a file dialog and updates after selection the displayed path
        directory and the check mark. Only .mmt files can be selected.
        """
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Model Files (*.mmt)", options=options)

        # check format of file
        self.is_model_file_valid = self._is_model_file_valid(file_path)

        if self.is_model_file_valid:
            # make model globally accessible
            self.model_file = file_path

            # update QLineEdit in the GUI to selected file
            self.model_path_text_field.setText(self.model_file)

            # update check mark
            self.model_check_mark.setPixmap(self.main_window.rescaled_cm)

            # update model display
            with open(self.model_file, 'r') as model_file:
                contents = model_file.read()
                self.model_display_text_field.setText(contents)

            # close select model window
            self.model_selection_window.close()
        else:
            # generate error message
            error_message = 'The selected model file is invalid! Please, select a model from the library or choose a valid model file.'
            QtWidgets.QMessageBox.question(self, 'Model file invalid!', error_message, QtWidgets.QMessageBox.Yes)


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