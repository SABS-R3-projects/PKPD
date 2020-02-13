import os

import numpy as np
import pandas as pd
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
        """Creates the model file dialog group consisting of a label, the model selection group and a display window of the model .mmt file.

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
        """Creates the model selection group consisting of a 'select model' button, that opens a model selection window, a
        text field detailing further information about the model and an image response to the validity of the chosen model.

        Returns:
            {QGroupBox} -- Returns model selection group object.
        """
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
        """Creates model selection window consisting of the model library and buttons to either choose a model
        from the library or from a local directory.
        """
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
        """Creates model library, consisting of dropdown menus detailing the properties of the models.

        Returns:
            {QGroupBox} -- Returns model library group object.
        """
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
        """Creates number of compartments dropdown menu.

        Returns:
            {QHBoxLayout} -- Returns dropdown menu with label.
        """
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
        """Creates dose type dropdown menu.

        Returns:
            {QHBoxLayout} -- Returns dropdown menu with label.
        """
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
        """Creates transition rates dropdown menu.

        Returns:
            {QHBoxLayout} -- Returns dropdown menu with label.
        """
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
        """Creates model button group consisting of a 'select model', 'cancel' and 'select from file' button.
        'select model' selects the chosen model from the libray, 'cancel' closes the window and 'select from file'
        opens a file dialog.

        Returns:
            {QHBoxLayout} -- Returns model button group object.
        """
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
        """Creates display for the model .mmt file.

        Returns:
            {QHBoxLayout} -- Returns model display object.
        """
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
        height = 0.3 * self.main_window.height
        scroll.setFixedHeight(height)

        # arrange display window horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(scroll)

        return hbox


    def _create_data_group(self):
        """Creates the data file dialog group consisting of a label, a button that opens the file dialog, a text field that displays
        the selected file and a check mark symbol that gives feedback whether or not the chosen file is valid.

        Returns:
            {QGroupBox} -- Returns data group object.
        """
        # Create group label
        group = QtWidgets.QGroupBox('Data:')

        # create data selection group
        data_selection_group = self._create_data_selection_group()

        # create display of csv file
        data_display = self._create_data_display()

        # create data format check box group
        check_box_group = self._create_check_box_group()

        # arrange button/text and label vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(data_selection_group)
        vbox.addLayout(data_display)
        vbox.addLayout(check_box_group)

        group.setLayout(vbox)

        return group


    def _create_data_selection_group(self):
        """Creates the data selection group consisting of a 'select data' button, that opens a file dialog, a
        text field displaying the path to the data file and an image response to the validity of the chosen file.

        Returns:
            {QGroupBox} -- Returns a data selection group object.
        """
        # create data selection button
        button = QtWidgets.QPushButton('select data file')
        button.clicked.connect(self.on_data_click)

        # display path to model file
        self.data_path_text_field = QtWidgets.QLineEdit('no file selected')

        # make text field non-editable
        self.data_path_text_field.setReadOnly(True)

        # create file check mark
        self.data_check_mark = self._create_file_check_mark()

        # arange button and text horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(button)
        hbox.addWidget(self.data_path_text_field)
        hbox.addWidget(self.data_check_mark)

        return hbox


    def _create_data_display(self):
        """Creates display for the data .csv file.

        Returns:
            {QHBoxLayout} -- Returns data display object.
        """
        # create text field to display data
        self.data_display = QtWidgets.QTableView()

        # adjust color of text field
        self.data_display.setStyleSheet("background-color: rgb(128,128,128);")

        # # make text field non-editable
        # self.data_display.setReadOnly(True)

        # make display scrollable, such that window is never exceeded
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.data_display)
        scroll.setWidgetResizable(True)

        # fix vertical space that display can take up
        height = 0.3 * self.main_window.height
        scroll.setFixedHeight(height)

        # arange display window horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(scroll)

        return hbox


    def _create_check_box_group(self):
        """Creates check boxes for the presence of patient IDs and doses in the data set.

        Returns:
            {QHBoxLayout} -- Returns check box group object.
        """
        # create check box for presence of patient ID data
        self.patient_id_check_box = QtWidgets.QCheckBox('Patient ID provided')
        self.patient_id_check_box.stateChanged.connect(self.on_check_box_click)

        # create check box for presence of doses in data
        self.dose_schedule_check_box = QtWidgets.QCheckBox('Dosing provided')
        self.dose_schedule_check_box.stateChanged.connect(self.on_check_box_click)

        # arange check boxes horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.patient_id_check_box)
        hbox.addWidget(self.dose_schedule_check_box)
        hbox.addStretch(1)

        return hbox


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
        """Reaction to clicking the 'select model' button in the home tab. Opens the model selection window.
        """
        self.model_selection_window.open()


    @QtCore.pyqtSlot()
    def on_model_select_click(self):
        """Reaction to clicking the 'select model' button in the model selection window. Gets model file,
        updates the model text field and the model display.
        """
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
        """Closes the model selection window.
        """
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


    def _is_model_file_valid(self, file_path:str) -> bool:
        """Checks the validity of the chosen model file.

        Arguments:
            file_path {str} -- path to model file.
        
        Returns:
            {bool} -- True if valid, False if invalid.
        """
        # check existence
        is_file_existent = os.path.isfile(file_path)

        # check format
        is_format_correct = file_path.split('.')[-1] == 'mmt'

        # are both citeria satisifed
        is_path_valid = is_file_existent and is_format_correct

        return is_path_valid


    @QtCore.pyqtSlot()
    def on_data_click(self):
        """Opens a file dialog and updates after selection the displayed path directory, as well as the dosplay window and the check mark.
        Only .csv files can be selected.
        """
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Data Files (*.csv)", options=options)

        # check format of file
        self.is_data_file_valid = self._is_data_file_valid(file_path)

        if self.is_data_file_valid:
            # make model globally accessible
            self.data_file = file_path

            # read in data file
            self.data_df = pd.read_csv(file_path, na_values=['.'])

            # update QLineEdit in the GUI to selected file
            self.data_path_text_field.setText(file_path)

            # update check mark
            self.data_check_mark.setPixmap(self.main_window.rescaled_cm)

            # check presence of patient IDs/doses and update check boxes
            self._update_check_boxes()

            # TODO:
            # 1. color the columns in the display according to their meaning/ indicate that the program things that they are different things
            # 2. merge Rebeccas stuff into this branch
            # 3. improve the data handling based on the information that is now already available.

            # update data display
            self.data_display.setModel(PandasModel(self.data_df, self.patient_id_check_box.isChecked(), self.dose_schedule_check_box.isChecked()))

            # make content fill the reserved space of the table view
            self.data_display.resizeColumnsToContents()
        else:
            # generate error message
            error_message = 'The selected data file is invalid! Please, try again.'
            QtWidgets.QMessageBox.question(self, 'Data file invalid!', error_message, QtWidgets.QMessageBox.Yes)


    def _is_data_file_valid(self, file_path:str) -> bool:
        """Checks the validity of the chosen model file.

        Arguments:
            file_path {str} -- path to model file.
        
        Returns:
            {bool} -- True if valid, False if invalid.
        """
        # check existence
        is_file_existent = os.path.isfile(file_path)

        # check format
        is_format_correct = file_path.split('.')[-1] == 'csv'

        # are both citeria satisifed
        is_path_valid = is_file_existent and is_format_correct

        return is_path_valid


    def _update_check_boxes(self):
        """Updates the data check boxes based on the data's properties.
        """
        # check for presence of patient IDs in first column
        self._check_data_for_patient_IDs()

        # check for presence of doses in last column
        self._check_data_for_doses()


    def _check_data_for_patient_IDs(self):
        """Checks whether patient IDs are provided in dataframe. Patient IDs are assumed to be present, if first column only consists of integer values.
        """
        # expected data type for patient IDs
        expected_data_type = 'int64'

        # get first column of data frame
        first_column = self.data_df.iloc[:, 0]

        # set check box to be ticked, if data types coincide
        is_data_type_equal = expected_data_type == first_column.dtypes
        self.patient_id_check_box.setChecked(is_data_type_equal)


    def _check_data_for_doses(self):
        """Checks whether dosing schedule is provided in dataframe and removes trailing empty columns.
        """
        # get the last non-empty column
        is_last_column_empty = True
        while is_last_column_empty:
            # get last column in dataframe
            last_column = self.data_df.iloc[:, -1]

            # check whether column is empty
            is_last_column_empty = last_column.dropna().empty

            # drop empty column
            if is_last_column_empty:
                # get data keys
                keys = self.data_df.keys()

                # remove last column
                self.data_df.drop(columns=[keys[-1]], inplace=True)

        # check whether last column has format expected from dosing schedule
        is_data_format_as_expected = self._dose_format_check(last_column)

        # update check box
        self.dose_schedule_check_box.setChecked(is_data_format_as_expected)


    def _dose_format_check(self, last_column:pd.Series()):
        """Hereustic method to check whether format coincides with the one expected from a dosing schedule (checks whether meaningful entries are evenly spaced).

        Arguments:
            last_column {pd.Series} -- Last non-empty column of dataframe.
        """
        # create mask for meaningful entries
        mask_meaningful_entries = last_column.notnull()

        # get meaningful entries' indices
        indices = np.array(last_column.index[mask_meaningful_entries])

        # if first two meaningful entries follow each other, the column is assumed to contain data
        if indices[1] == 1:
            return False

        # check whether their spacing is regular
        is_equally_spaced = np.all(indices[1] == np.diff(indices))

        return is_equally_spaced


    @QtCore.pyqtSlot()
    def on_check_box_click(self):
        # update data display
        self.data_display.setModel(PandasModel(self.data_df, self.patient_id_check_box.isChecked(), self.dose_schedule_check_box.isChecked()))

        # make content fill the reserved space of the table view
        self.data_display.resizeColumnsToContents()


    @QtCore.pyqtSlot()
    def on_next_click(self):
        """Executes the MainWindow.next_tab method.
        """
        self.main_window.next_tab()


###### TO BE REMOVED ####
class PandasModel(QtCore.QAbstractTableModel):

    def __init__(self, data, is_id_present, is_dosing_present):
        QtCore.QAbstractTableModel.__init__(self)
        self._data = data
        self._is_id_present = is_id_present
        self._is_dosing_present = is_dosing_present

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])

            if self._is_id_present:
                # color id column blue grey
                if role == QtCore.Qt.BackgroundRole and index.column() == 0:
                    return QtGui.QBrush(QtGui.QColor(60, 60.4, 89.8))

                # color time column (darker) grey
                if role == QtCore.Qt.BackgroundRole and index.column() == 1:
                    return QtGui.QBrush(QtGui.QColor(69.8, 69.8, 69.8))
            else:
                # color time column (darker) grey
                if role == QtCore.Qt.BackgroundRole and index.column() == 0:
                    return QtGui.QBrush(QtGui.QColor(69.8, 69.8, 69.8))

            if self._is_dosing_present:
                last_column_id = self.columnCount()-1
                # color last column red grey
                if role == QtCore.Qt.BackgroundRole and index.column() == last_column_id:
                    return QtGui.QBrush(QtGui.QColor(89.8, 60, 61.2))

        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None