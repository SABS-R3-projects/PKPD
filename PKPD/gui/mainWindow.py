import os
import sys
from typing import List

from PyQt5 import QtCore, QtWidgets, QtGui

from PKPD.gui import abstractGui, home

class MainWindow(abstractGui.AbstractMainWindow):
    """MainWindow class which sets up basic functionality, the general geometry and layout of the GUI.
    """
    def __init__(self, app):
        """Initialises the main window.
        """
        super().__init__()
        self.app = app
        self.window_title = 'Pharmacokinetics/Pharmacodynamics'
        self.version_number = QtWidgets.QLabel('Version: 0.0.0')
        self.producers = QtWidgets.QLabel('SABS R3')
        # variables needed across tabs
        # self.model_file = None
        # self.data_file = None
        self.available_geometry = self.app.desktop().availableGeometry()
        _, _, self.desktop_width, self.desktop_height = self.available_geometry.getRect()
        # set window size.
        self._set_window_size()
        # format icons/images
        self._format_images()
        # fill the empty window with content
        self._arrange_window_content()


    def _set_window_size(self):
        """Keeps an aspect ratio width / height of 5/4 and scales the width such that 0.75 of the screen width is covered. If this
        leads to a window height exceeding the screen height, the aspect ratio is kept and the window height is set to the screen
        height.
        """
        width_coverage = 0.75 # subjective aesthetical choice
        aspect_ratio = 5 / 4 # subjective aesthetical choice

        # sanity check
        if (self.desktop_width < 1) or (self.desktop_height < 1):
            raise ValueError('Resolution of desktop appears to be too low, i.e. less than a pixel for either width or height.')

        self.width = int(self.desktop_width * width_coverage)
        self.height = int(self.width / aspect_ratio)

        # check whether window with 0.75 desktop width fits on screen, else rescale.
        if self.height > self.desktop_height:
            self.height = self.desktop_height
            self.width = int(self.height * aspect_ratio)

        # update window size
        size = self.size()
        size.setWidth(self.width)
        size.setHeight(self.height)

        self.setGeometry(QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            size,
            self.available_geometry
            )
        )


    def _format_images(self):
        """Scales images and logos according to the desktop size.
        """
        # SABS R3 logo in status bar
        sabs_logo = QtGui.QPixmap('images/SABSR3.png')
        self.rescaled_sabs = sabs_logo.scaledToHeight(self.desktop_height * 0.02)
        # symbols for success/failure of file selection
        question_mark = QtGui.QPixmap('images/QUESTION.png')
        self.rescaled_qm = question_mark.scaledToHeight(self.desktop_height * 0.025)
        check_mark = QtGui.QPixmap('images/CHECK.png')
        self.rescaled_cm = check_mark.scaledToHeight(self.desktop_height * 0.025)
        red_cross = QtGui.QPixmap('images/FALSE.png')
        self.rescaled_rc = red_cross.scaledToHeight(self.desktop_height * 0.03)


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
        self.home = home.HomeTab(self)
        self.simulation = SimulationTab(self)
        # add tabs to tab widget.
        tabs = QtWidgets.QTabWidget()
        self.home_tab_index = tabs.addTab(self.home, self.home.name)
        self.sim_tab_index = tabs.addTab(self.simulation, self.simulation.name)

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
        """Creates SABS R3 logo in the status bar.

        Returns:
            {QLabel} -- Returns SABS R3 logo.
        """
        label = QtWidgets.QLabel(self)
        label.setPixmap(self.rescaled_sabs)

        return label


    def next_tab(self):
        """Switches to the simulation tab, when triggered by clicking the 'next' QPushButton on the home tab.
        """
        correct_model, correct_data = self._file_sanity_check()
        if correct_model and correct_data:
            # plot data in simulation tab
            self.simulation.add_data_to_data_model_plot()
            # instantiate model and inverse problem
            self.model = m.SingleOutputModel(self.model_file)
            self.problem = inf.SingleOutputInverseProblem(model=self.model,
                                                          times=self.simulation.time_data,
                                                          values=self.simulation.state_data)
            self.simulation.create_parameter_sliders()
            self.simulation.create_parameter_table()
            # switch to simulation tab
            self.tabs.setCurrentIndex(self.sim_tab_index)
        else:
            # update file dialog icons
            if not correct_model:
                self.home.model_check_mark.setPixmap(self.rescaled_rc)
            else:
                self.home.model_check_mark.setPixmap(self.rescaled_cm)
            if not correct_data:
                self.home.data_check_mark.setPixmap(self.rescaled_rc)
            else:
                self.home.data_check_mark.setPixmap(self.rescaled_cm)
            # generate error message
            error_message = 'At least one of the files does not seem to exist or does not have the correct file format. Please check again!'
            QtWidgets.QMessageBox.question(self, 'Files not found!', error_message, QtWidgets.QMessageBox.Yes)


    def _file_sanity_check(self) -> List[bool]:
        """Checks whether model and data exist and have the correct format (.mmt and .csv, respectively).

        Returns:
            {List[bool]} -- Returns flags for the model and data file.
        """
        # model sanity check
        self.model_file = self.home.model_text.text()
        model_is_file = os.path.isfile(self.model_file)
        model_correct_format = self.model_file.split('.')[-1] == 'mmt'
        correct_model = model_is_file and model_correct_format
        # data sanity check
        self.data_file = self.home.data_text.text()
        data_is_file = os.path.isfile(self.data_file)
        data_correct_format = self.data_file.split('.')[-1] == 'csv'
        correct_data = data_is_file and data_correct_format

        return [correct_model, correct_data]


##################################################################################
# to be moved to simulation.py
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PKPD.model import model as m
from PKPD.inference import inference as inf

class SimulationTab(QtWidgets.QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.name = 'Simulation'
        self.main_window = main_window
        self.enable_live_plotting = False
        self.parameter_values = None

        # a figure instance to plot on
        data_model_figure = Figure()
        self.data_model_ax = data_model_figure.add_subplot(111)
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(data_model_figure)

        # set the layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(self.infer_plot_model())
        self.setLayout(layout)

    def add_data_to_data_model_plot(self):
        # TODO: so far only 1d models can be handeled.
        # load data
        data = pd.read_csv(self.main_window.data_file)
        # sort into time and state data
        time_label, state_label = data.keys()[0], data.keys()[1]
        self.time_data = data[time_label].to_numpy()
        self.state_data = data[state_label].to_numpy()
        # plot data
        # TODO: add separate different compartments into different subplots
        self.data_model_ax.clear()
        self.data_model_ax.scatter(x=self.time_data, y=self.state_data, label='data', marker='o', color='darkgreen', edgecolor='black',
                   alpha=0.5)
        self.data_model_ax.set_xlabel(time_label)
        self.data_model_ax.set_ylabel(state_label)
        self.data_model_ax.legend()

        # refresh canvas
        self.canvas.draw()


    def infer_plot_model(self):
        #TODO: make sliders and plot button
        # initialise sliders, 'plot model' button,'infer model' button and
        # infered parameters table
        self.parameter_sliders = QtWidgets.QGridLayout()
        plot_button = QtWidgets.QPushButton('plot model')
        plot_button.clicked.connect(self.on_plot_model_click)
        infer_button = QtWidgets.QPushButton('infer model')
        infer_button.clicked.connect(self.on_infer_model_click)
        self.infered_parameter_table = QtWidgets.QTableWidget()

        # arange plot and widgets vertically
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addLayout(self.parameter_sliders)
        vertical_layout.addWidget(plot_button)
        vertical_layout.addWidget(infer_button)
        vertical_layout.addWidget(self.infered_parameter_table)

        return vertical_layout


    def create_parameter_sliders(self):
        # TODO: replace internal parameter names by description.
        state_name = self.main_window.model.state_name
        model_param_names = self.main_window.model.parameter_names
        parameter_names = [state_name] + model_param_names

        # fill up grid with slider objects
        self.slider_container = [] # store in to list to be able to update later individually
        self.parameter_text_field_container = []
        for param_id, param_name in enumerate(parameter_names):
            self.parameter_sliders.addWidget(self._create_slider(param_name), param_id, 0)

        # container to store parameter values
        self.parameter_values = np.empty(len(self.parameter_text_field_container))


    def _create_slider(self, parameter_name):
        slider_box = QtWidgets.QGroupBox(parameter_name)
        # make horizontal slider
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        # keep track of slider by adding it to container
        self.slider_container.append(slider)
        # create labels
        min_current_max_value = self._display_min_current_max_value()
        slider.valueChanged[int].connect(self._update_parameter_values)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(slider)
        vbox.addLayout(min_current_max_value)
        vbox.addStretch(1)
        slider_box.setLayout(vbox)

        return slider_box


    def _display_min_current_max_value(self):
        slider = self.slider_container[-1]
        min_value = QtWidgets.QLabel('0')
        text_field = QtWidgets.QLineEdit(str(slider.value()))
        max_value = QtWidgets.QLabel('10')
        # keep track of parameter values
        self.parameter_text_field_container.append(text_field)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(min_value)
        hbox.addStretch(1)
        hbox.addWidget(text_field)
        hbox.addStretch(1)
        hbox.addWidget(max_value)

        return hbox


    def _update_parameter_values(self):
        # for lack of creativity just update all parameters
        for slider_id, slider in enumerate(self.slider_container):
            self.parameter_values[slider_id] = slider.value()
            self.parameter_text_field_container[slider_id].setText(str(self.parameter_values[slider_id]))

        if self.enable_live_plotting:
            self._plot_model()


    def create_parameter_table(self):
        # get fit parameter names
        state_name = self.main_window.model.state_name
        model_param_names = self.main_window.model.parameter_names
        parameter_names = [state_name] + model_param_names
        number_parameters = len(parameter_names)

        # fill up table with parameter columns (name and empty cell)
        self.infered_parameter_table.setRowCount(1)
        self.infered_parameter_table.setColumnCount(number_parameters)
        for param_id, param_name in enumerate(parameter_names):
            self.infered_parameter_table.setHorizontalHeaderItem(param_id, QtWidgets.QTableWidgetItem(param_name))
            self.infered_parameter_table.setItem(0, param_id, QtWidgets.QTableWidgetItem(''))

        # set height and width of table to fit the content
        header_height = self.infered_parameter_table.horizontalHeader().height()
        cell_height = self.infered_parameter_table.rowHeight(0)
        self.infered_parameter_table.setMaximumHeight(header_height + cell_height)
        header_width = self.infered_parameter_table.verticalHeader().width()
        cell_width = self.infered_parameter_table.columnWidth(0)
        self.infered_parameter_table.setMaximumWidth(header_width + number_parameters * cell_width)


    def _plot_model(self):
        self.state_values = self.main_window.model.simulate(parameters=self.parameter_values,
                                                            times=self.times
                                                            )
        if self.enable_line_removal:
            self.data_model_ax.lines.pop()
        # plot current values
        self.data_model_ax.plot(self.times, self.state_values, linestyle='dashed', color='grey')
        # refresh canvas
        self.canvas.draw()


    @QtCore.pyqtSlot()
    def on_plot_model_click(self):
        # define time points for evaluation and container for simulation
        self.times = np.linspace(start=self.time_data[0],
                            stop=self.time_data[-1],
                            num=100
                            )
        for param_id, param_text_field in enumerate(self.parameter_text_field_container):
            self.parameter_values[param_id] = float(param_text_field.text())
        self.state_values = np.empty(len(self.times))

        # enable live plotting with sliders
        self.enable_live_plotting = True
        # disable removal of previous line (either there is none or its the infered model)
        self.enable_line_removal = False

        # plot model
        self._plot_model()

        # enable removal of plots again to prevent fludding of figure
        self.enable_line_removal = True


    # TODO:
    # - make infered parameters visible somewhere
    # - display correct min and max value
    # - let inference start from chosen parameter values
    # - create double click option to adjust range of slider
    #   and tick option whether range is supposed to constrain inference
    # - create warning when infer parameters is clicked multiple times
    # - if yes delete infered model and do inference again
    # - create warning when plot model is clicked without having
    #   adjusted the model parameters.
    # - fix the window size, such that slider doesnt affect window




    @QtCore.pyqtSlot()
    def on_infer_model_click(self):
        # disable live model plotting
        self.enable_live_plotting = False

        # TODO: make this compatible with multi-output models
        initial_parameters = np.array([25, 3, 5])

        # find parameters
        self.main_window.problem.find_optimal_parameter(initial_parameter=initial_parameters)
        self.estimated_parameters = self.main_window.problem.estimated_parameters

        # plot infered model
        self._plot_infered_model()

        # update parameter table
        self._update_parameter_table()



    def _plot_infered_model(self):
        times = np.linspace(start=self.time_data[0],
                            stop=self.time_data[-1],
                            num=100
                            )
        state_values = self.main_window.model.simulate(parameters=self.main_window.problem.estimated_parameters,
                                                       times=times
                                                       )
        self.data_model_ax.plot(times, state_values, color='black', label='model')
        self.data_model_ax.legend()

        # refresh canvas
        self.canvas.draw()


    def _update_parameter_table(self):
        for param_id, param_value in enumerate(self.estimated_parameters):
            self.infered_parameter_table.item(0, param_id).setText('%.3f' % param_value)


###################################################################################


if __name__ == '__main__':

    # Create window instance
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)

    # show window
    window.show()
    sys.exit(app.exec_())