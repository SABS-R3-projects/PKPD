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
            # disable live plotting and line removal for the simulation
            self.simulation.enable_live_plotting = False
            self.simulation.enable_line_removal = False

            # instantiate model and inverse problem
            if self.simulation.is_single_output_model:
                self.model = m.SingleOutputModel(self.model_file)
                self.problem = inf.SingleOutputInverseProblem(model=self.model,
                                                              times=self.simulation.time_data,
                                                              values=self.simulation.state_data)
            else:
                self.model = m.MultiOutputModel(self.model_file)
                self.problem = inf.MultiOutputInverseProblem(model=self.model,
                                                             times=self.simulation.time_data,
                                                             values=self.simulation.state_data)
            self.simulation.fill_parameter_slider_group()
            self.simulation.fill_plot_option_window()
            self.simulation.fill_parameter_table()

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
import pints
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PKPD.model import model as m
from PKPD.inference import inference as inf

class SimulationTab(QtWidgets.QDialog):
    """Simulation tab class that is responsible for plotting the data and the model, as well as providing
    the ability to infer an optimal set model parameters for the data set.
    """
    def __init__(self, main_window):
        super().__init__()
        self.name = 'Simulation'
        self.main_window = main_window
        self.enable_live_plotting = False
        self.enable_line_removal = False
        self.is_single_output_model = True
        self.parameter_values = None

        # initialising the figure
        self.data_model_figure = Figure()
        self.canvas = FigureCanvas(self.data_model_figure)

        # set the layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(self._init_plot_infer_model_group())
        self.setLayout(layout)


    def add_data_to_data_model_plot(self):
        """Adds the data from the in the home tab chosen data file to the previously initialised figure. For multi-
        dimensional data, the figure is split into subplots.
        """
        # load data
        data = pd.read_csv(self.main_window.data_file)
        time_label, state_labels = data.keys()[0], data.keys()[1:]

        # check dimensionality of problem for plotting and inference
        self.state_dimension = len(state_labels)
        self.is_single_output_model = self.state_dimension == 1

        # sort into time and state data
        self.time_data = data[time_label].to_numpy()
        if self.is_single_output_model:
            state_label = state_labels[0]
            self.state_data = data[state_label].to_numpy()
        else:
            self.state_data = data[state_labels].to_numpy()

        # plot data
        if self.is_single_output_model: # single output
            # clear figure
            self.data_model_figure.clf()

            # create plot
            self.data_model_ax = self.data_model_figure.subplots()
            self.data_model_ax.scatter(x=self.time_data, y=self.state_data, label='data', marker='o', color='darkgreen',
                                       edgecolor='black', alpha=0.5)
            self.data_model_ax.set_xlabel(time_label)
            self.data_model_ax.set_ylabel(state_label)
            self.data_model_ax.legend()

            # refresh canvas
            self.canvas.draw()
        else: # multi output
            # clear figure
            self.data_model_figure.clf()

            # create subplots for each compartment
            self.data_model_ax = self.data_model_figure.subplots(nrows=self.state_dimension, sharex=True)
            for dim in range(self.state_dimension):
                self.data_model_ax[dim].scatter(x=self.time_data, y=self.state_data[:, dim], label='data', marker='o',
                                                color='darkgreen', edgecolor='black', alpha=0.5)
                self.data_model_ax[dim].set_ylabel(state_labels[dim])
                self.data_model_ax[dim].legend()
            self.data_model_ax[-1].set_xlabel(time_label)

            # refresh canvas
            self.canvas.draw()


    def _init_plot_infer_model_group(self):
        """Initialises the functional sliders and buttons of the simulation tab.

        Returns:
            vbox {QVBoxLayout} -- Returns the layout arranging the sliders, buttons and the inferred parameter table.
        """
        # initialise sliders, 'plot model' button,'infer model' button and inferred parameters table
        slider_group = self._initialise_slider_group()
        plot_buttons = self._initialise_plot_buttons()
        infer_buttons = self._initialise_infer_buttons()
        self.inferred_parameter_table = QtWidgets.QTableWidget()

        # arrange widgets vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(slider_group)
        vbox.addLayout(plot_buttons)
        vbox.addLayout(infer_buttons)
        vbox.addWidget(self.inferred_parameter_table)

        return vbox


    def _initialise_slider_group(self):
        """Initialises the value sliders for the model parameters.

        Returns:
            scroll {QScrollArea} -- Returns an area of fixed, relative size to the app screen that is scrollable
                                    should the slider group exceed the assigned space.
        """
        # initialise slider group widget
        slider_group = QtWidgets.QGroupBox()

        # initialise grid to arrange sliders vertically
        self.parameter_sliders = QtWidgets.QGridLayout()

        # add grid layout to slider group
        slider_group.setLayout(self.parameter_sliders)

        # make slider group scrollable, such that window is never exceeded
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(slider_group)
        scroll.setWidgetResizable(True)

        # fix vertical space that sliders can take up
        height = 0.7 * self.main_window.height
        scroll.setFixedHeight(height)

        return scroll


    def _initialise_plot_buttons(self):
        # create plot model button
        plot_button = QtWidgets.QPushButton('plot model')
        plot_button.clicked.connect(self.on_plot_model_click)

        # create option button
        option_button = QtWidgets.QPushButton('option')
        option_button.clicked.connect(self.on_plot_option_click)

        # initialise option window
        self.plot_option_window = QtWidgets.QDialog()

        # arange button horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(plot_button)
        hbox.addWidget(option_button)

        return hbox


    def _initialise_infer_buttons(self):
        # create plot model button
        infer_button = QtWidgets.QPushButton('infer model')
        infer_button.clicked.connect(self.on_infer_model_click)

        # create option button
        option_button = QtWidgets.QPushButton('option')
        option_button.clicked.connect(self.on_infer_option_click)

        # create option window
        self._create_infer_option_window()

        # arange button horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(infer_button)
        hbox.addWidget(option_button)

        return hbox


    def _create_infer_option_window(self):
        """Creates an option window to set the inference settings.
        """
        # create option window
        self.infer_option_window = QtWidgets.QDialog()
        self.infer_option_window.setWindowTitle('Inference options')

        # define dropdown dimension
        self.dropdown_menu_width = 190 # value arbitrary

        # create inference options
        optimiser_options = self._create_optimiser_options()
        objective_function_options = self._create_objective_function_options()

        # create apply / cancel buttons
        apply_cancel_buttons = self._create_apply_cancel_buttons()

        # arange options vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(optimiser_options)
        vbox.addLayout(objective_function_options)
        vbox.addLayout(apply_cancel_buttons)

        # add options to window
        self.infer_option_window.setLayout(vbox)


    def _create_optimiser_options(self):
        """Creates a dropdown menu to select an optimiser method for the inference.

        Returns:
            hbox {QHBoxLayout} -- Returns label and dropdown menu.
        """
        # create label
        label = QtWidgets.QLabel('selected optimiser:')

        # define options
        valid_optimisers = ['CMA-ES', 'Nelder-Mead', 'SNES', 'xNES']

        # create dropdown menu for options
        self.optimiser_dropdown_menu = QtWidgets.QComboBox()
        self.optimiser_dropdown_menu.setMinimumWidth(self.dropdown_menu_width)
        for optimiser in valid_optimisers:
            self.optimiser_dropdown_menu.addItem(optimiser)

        # arange label and dropdown menu horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.optimiser_dropdown_menu)

        return hbox


    def _create_objective_function_options(self):
        """Creates a dropdown menu to select an error measure for the inference.

        Returns:
            hbox {QHBoxLayout} -- Returns label and dropdown menu.
        """
        # create label
        label = QtWidgets.QLabel('selected error measure:')

        # define options
        valid_error_measures = ['Mean Squared Error', 'Sum of Squares Error']

        # create dropdown menu for options
        self.error_measure_dropdown_menu = QtWidgets.QComboBox()
        self.error_measure_dropdown_menu.setMinimumWidth(self.dropdown_menu_width)
        for error_measure in valid_error_measures:
            self.error_measure_dropdown_menu.addItem(error_measure)

        # arange label and dropdown menu horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.error_measure_dropdown_menu)

        return hbox


    def _create_apply_cancel_buttons(self):
        """Creates an apply and cancel button to either update the inference settings or
        closing the option window without updating.

        Returns:
            hbox {QHBoxLayout} -- Returns layout aranging the apply and cancel button.
        """
        # create apply and cancel button
        apply_button = QtWidgets.QPushButton('apply')
        apply_button.clicked.connect(self.on_infer_option_apply_click)
        cancel_button = QtWidgets.QPushButton('cancel')
        cancel_button.clicked.connect(self.on_infer_option_cancel_button_click)

        # arange buttons horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(apply_button)
        hbox.addWidget(cancel_button)

        return hbox


    @QtCore.pyqtSlot()
    def on_infer_option_apply_click(self):
        """Reaction to left-clicking the infer option 'apply' button. Updates the inference settings
        and closes the option window.
        """
        # update infer options
        self._set_optimiser()
        self._set_error_measure()

        # close option window
        self.infer_option_window.close()


    def _set_optimiser(self):
        """Sets the optimiser method for inference to the in the dropdown menu selected method.
        """
        # get selected optimiser
        optimiser = self.optimiser_dropdown_menu.currentText()

        # define dictionary between optimiser names and pints methods
        optimiser_dict = {'CMA-ES': pints.CMAES,
                          'Nelder-Mead': pints.NelderMead,
                          'SNES': pints.SNES,
                          'xNES': pints.XNES
                          }

        # get corresponding pints method
        method = optimiser_dict[optimiser]

        # update optimiser
        self.main_window.problem.set_optimiser(method)


    def _set_error_measure(self):
        """Sets the error measure for inference to the in the dropdown menu selected measure.
        """
        # get selected optimiser
        error_measure = self.error_measure_dropdown_menu.currentText()

        # define dictionary between error measure names and pints methods
        error_measure_dict = {'Mean Squared Error': pints.MeanSquaredError,
                              'Sum of Squares Error': pints.SumOfSquaresError,
                              }

        # get corresponding pints measure
        measure = error_measure_dict[error_measure]

        # update error measure
        self.main_window.problem.set_objective_function(measure)


    @QtCore.pyqtSlot()
    def on_infer_option_cancel_button_click(self):
        """Reaction to left-clicking the infer option 'cancel' button. Closes the window.
        """
        # close option window
        self.infer_option_window.close()


    def fill_parameter_slider_group(self):
        """Fills the initialised slider group with parameter sliders (the number of sliders is determined by the
        number of parameters in the model).
        """
        self._clear_slider_group()

        # get parameter names
        if self.is_single_output_model:
            state_names = [self.main_window.model.state_name]
        else:
            state_names = self.main_window.model.state_names
        model_param_names = self.main_window.model.parameter_names # parameters except initial conditions
        parameter_names = state_names + model_param_names # parameters including initial conditions

        # fill up grid with slider objects
        self.slider_container = [] # store in list to be able to update later
        self.slider_min_max_label_container = [] # store in list to be able to update later
        self.parameter_text_field_container = [] # store in list to be able to update later
        for param_id, param_name in enumerate(parameter_names):
            self.parameter_sliders.addWidget(self._create_slider(param_name), param_id, 0)

        # initialise container to store parameter values (for efficiency)
        number_parameters = len(self.parameter_text_field_container)
        self.parameter_values = np.empty(number_parameters)


    def _clear_slider_group(self):
        """Clears the slider group from pre-existing sliders.
        """
        number_items_in_group = self.parameter_sliders.count()
        for item_id in range(number_items_in_group):
            # setting an items parent to None deletes it, according to stackoverflow
            self.parameter_sliders.itemAtPosition(item_id, 0).widget().setParent(None)


    def _create_slider(self, parameter_name: str):
        """Creates slider group. Includes parameter label, value slider, value text field and labels for slider boundaries.

        Arguments:
            parameter_name {str} -- Parameter name for which the slider is created.
        
        Returns:
            slider_box {QGroupBox} -- Returns a widget containing labels, a value slider and a value text field for the parameter.
        """
        # initialise widget
        slider_box = QtWidgets.QGroupBox(parameter_name)

        # create horizontal slider
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0.1) # arbitrary choice
        slider.setValue(1) # default arbitrary, but it seems reasonable to avoid zero
        slider.setMaximum(30) # arbitrary choice
        slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)

        # keep track of sliders
        self.slider_container.append(slider)

        # create labels
        min_current_max_value = self._create_min_current_max_value_label(slider)
        slider.valueChanged[int].connect(self._update_parameter_values)

        # arrange slider and labels
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(slider)
        vbox.addLayout(min_current_max_value)
        vbox.addStretch(1)
        slider_box.setLayout(vbox)

        return slider_box


    def _create_min_current_max_value_label(self, slider:QtWidgets.QSlider):
        """Creates labels for a slider displaying the current position of the slider and the minimum and
        maximum value of the slider.

        Arguments:
            slider {QtWidgets.QSlider} -- Parameter slider.
        
        Returns:
            hbox {QHBoxLayout} -- Returns a layout arranging the slider labels.
        """
        # create min/max labels and text field for current value
        min_value = QtWidgets.QLabel(str(slider.minimum()))
        text_field = QtWidgets.QLineEdit(str(slider.value()))
        max_value = QtWidgets.QLabel(str(slider.maximum()))

        # keep track of parameter values and min/max labels
        self.parameter_text_field_container.append(text_field)
        self.slider_min_max_label_container.append([min_value, max_value])

        # arrange widgets horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(min_value)
        hbox.addStretch(1)
        hbox.addWidget(text_field)
        hbox.addStretch(1)
        hbox.addWidget(max_value)

        return hbox


    def _update_parameter_values(self):
        """Updates parameter text fields when slider position is moved and updates the model plot in the
        figure, should live plotting be enabled.
        """
        # update slider text fields
        for slider_id, slider in enumerate(self.slider_container):
            self.parameter_values[slider_id] = slider.value()
            self.parameter_text_field_container[slider_id].setText('%d' % self.parameter_values[slider_id])

        # plot model if live plotting is enabled
        if self.enable_live_plotting and self.is_single_output_model:
            self._plot_single_output_model()
        elif self.enable_live_plotting and not self.is_single_output_model:
            self._plot_multi_output_model()


    def fill_plot_option_window(self):
        # TODO: finish this!
        # create text fields
        for slider in self.slider_container:
            pass


    def fill_infer_option_window(self):
        # TODO: finish this!
        # create text fields
        for slider in self.slider_container:
            pass


    @QtCore.pyqtSlot()
    def on_plot_model_click(self):
        """Reaction to left-clicking the 'plot model' button. Enables the 'live plotting feature' and plots the
        model with parameters from the current slider positions.
        """
        # enable live plotting with sliders
        self.enable_live_plotting = True

        # define time points for evaluation
        self.times = np.linspace(start=self.time_data[0],
                                 stop=self.time_data[-1],
                                 num=100
                                 )

        # get current parameters from sliders
        for param_id, param_text_field in enumerate(self.parameter_text_field_container):
            self.parameter_values[param_id] = float(param_text_field.text())

        # plot model
        if self.is_single_output_model:
            self._plot_single_output_model()
        else:
            self._plot_multi_output_model()

        # enable removal of plots to prevent fludding of figure
        self.enable_line_removal = True


    def _plot_single_output_model(self):
        """Plots the model in dashed, grey lines.
        """
        # solve forward problem for current parameter set
        self.state_values = self.main_window.model.simulate(parameters=self.parameter_values,
                                                            times=self.times
                                                            )

        # remove previous graph to avoid fludding the figure
        if self.enable_line_removal:
            self.data_model_ax.lines.pop()

        # plot model
        self.data_model_ax.plot(self.times, self.state_values, linestyle='dashed', color='grey')

        # refresh canvas
        self.canvas.draw()


    def _plot_multi_output_model(self):
        """Plots the model in dashed, grey lines. Each state dimension is plotted to a separate subplot.
        """
        # solve forward problem for current parameter set
        self.state_values = self.main_window.model.simulate(parameters=self.parameter_values,
                                                            times=self.times
                                                            )

        # remove previous graphs from subplots to avoid fludding the figure
        if self.enable_line_removal:
            for dim in range(self.state_dimension):
                self.data_model_ax[dim].lines.pop()

        # plot model
        for dim in range(self.state_dimension):
            self.data_model_ax[dim].plot(self.times, self.state_values[:, dim], linestyle='dashed', color='grey')

        # refresh canvas
        self.canvas.draw()


    @QtCore.pyqtSlot()
    def on_plot_option_click(self):
        """Reaction to left-clicking the plot 'option' button. Opens the plot option window.
        """
        # open option window
        self.plot_option_window.open()


    @QtCore.pyqtSlot()
    def on_infer_option_click(self):
        """Reaction to left-clicking the inference 'option' button. Opens the plot option window.
        """
        # open option window
        self.infer_option_window.open()


    def fill_parameter_table(self):
        """Fills the parameter table with # parameters columns. Each column carries the name of the respective parameter and an
        empty cell for the inferred value.
        """
        # get fit parameter names
        if self.is_single_output_model:
            state_names = [self.main_window.model.state_name]
        else:
            state_names = self.main_window.model.state_names
        model_param_names = self.main_window.model.parameter_names
        parameter_names = state_names + model_param_names
        number_parameters = len(parameter_names)

        # fill up table with parameter columns (name and empty cell)
        self.inferred_parameter_table.setRowCount(1)
        self.inferred_parameter_table.setColumnCount(number_parameters)
        for param_id, param_name in enumerate(parameter_names):
            self.inferred_parameter_table.setHorizontalHeaderItem(param_id, QtWidgets.QTableWidgetItem(param_name))
            self.inferred_parameter_table.setItem(0, param_id, QtWidgets.QTableWidgetItem(''))

        # set height and width of table to fit the content
        header_height = self.inferred_parameter_table.horizontalHeader().height()
        cell_height = self.inferred_parameter_table.rowHeight(0)
        self.inferred_parameter_table.setMaximumHeight(header_height + cell_height)
        header_width = self.inferred_parameter_table.verticalHeader().width()
        cell_width = self.inferred_parameter_table.columnWidth(0)
        self.inferred_parameter_table.setMaximumWidth(header_width + number_parameters * cell_width)


    @QtCore.pyqtSlot()
    def on_infer_model_click(self):
        """Reaction to left-clicking the 'infer model' button. A parameter set for the model is estimated that minimises an objective function
        with respect to the data. The initial point for the inference is taken from the slider position, and the inferred parameter set updates
        the sliders and the inferred parameter table.
        """
        # disable live plotting
        self.enable_live_plotting = False

        # disable line removal
        self.enable_line_removal = False

        # get initial parameters from slider text fields
        initial_parameters = []
        for parameter_text_field in self.parameter_text_field_container:
            value = float(parameter_text_field.text())
            initial_parameters.append(value) # Note: order of text fields matches order of params in inverse problem class

        # set parameter boundaries
        self._set_parameter_boundaries(initial_parameters)

        # if initial parameters lie within provided boundaries, start inference
        if self.correct_initial_values:
            # find parameters
            self.main_window.problem.find_optimal_parameter(initial_parameter=initial_parameters)
            self.estimated_parameters = self.main_window.problem.estimated_parameters

            # plot infered model
            self._plot_infered_model()

            # update slider position to infered parameters
            self._update_sliders_to_inferred_params()

            # update parameter table
            self._update_parameter_table()


    def _set_parameter_boundaries(self, initial_parameters:np.ndarray):
        """Gets slider boundaries and restricts the parameter search to those intervals. If initial parameters lie outside the domain of
        support, an error message is returned.

        Arguments:
            initial_parameters {np.ndarray} -- Initial point in parameter space for the inference.
        """
        # get boundaries from sliders
        min_values = []
        max_values = []
        for param_id, slider in enumerate(self.slider_container):
            minimum = slider.minimum()
            maximum = slider.maximum()
            initial_value = initial_parameters[param_id]

            # check whether initial value lies within boundaries
            if (initial_value < minimum) or (initial_value > maximum):
                # flag that there is problem with the initial values
                self.correct_initial_values = False

                # generate error message
                error_message = 'Initial parameters do not lie within boundaries. Please check again!'
                QtWidgets.QMessageBox.question(self, 'Parameters outside boundaries!', error_message, QtWidgets.QMessageBox.Yes)
                break
            else:
                # flag that initial values are correct
                self.correct_initial_values = True

                # collect boundaries
                min_values.append(slider.minimum())
                max_values.append(slider.maximum())

        # set boundaries for inference
        if self.correct_initial_values:
            self.main_window.problem.set_parameter_boundaries([min_values, max_values])


    def _plot_infered_model(self):
        """Plots inferred model in a solid, black line and removes all other lines from figure.
        """
        # define time points for model evaluation
        times = np.linspace(start=self.time_data[0],
                            stop=self.time_data[-1],
                            num=100
                            )

        # solve forward problem
        state_values = self.main_window.model.simulate(parameters=self.main_window.problem.estimated_parameters,
                                                       times=times
                                                       )
        if self.is_single_output_model: # single-output problem
            # remove all lines from figure
            lines = self.data_model_ax.lines
            while lines:
                lines.pop()

            # plot model
            self.data_model_ax.plot(times, state_values, color='black', label='model')
            self.data_model_ax.legend()
        else: # multi-output problem
            # remove all lines from figure
            for dim in range(self.state_dimension):
                lines = self.data_model_ax[dim].lines
                while lines:
                    lines.pop()

            # plot model
            for dim in range(self.state_dimension):
                self.data_model_ax[dim].plot(times, state_values[:, dim], color='black', label='model')
                self.data_model_ax[dim].legend()

        # refresh canvas
        self.canvas.draw()


    def _update_sliders_to_inferred_params(self):
        """Set slider positions and text fields to inferred parameters.
        """
        for param_id, param_value in enumerate(self.estimated_parameters):
            slider = self.slider_container[param_id]
            slider.setValue(param_value)
            text_field = self.parameter_text_field_container[param_id]
            text_field.setText('%d' % int(param_value))


    def _update_parameter_table(self):
        """Fills parameter table cells with inferred parameter values.
        """
        for param_id, param_value in enumerate(self.estimated_parameters):
            self.inferred_parameter_table.item(0, param_id).setText('%.3f' % param_value)



# TODO:
# - documentation
# - make option button for plotting
#   - choose range of sliders and resolution
# - make option button for inference
#   - choice of objective fuction
#   - choice of optimiser
#   - choice whether parameters should be constrained by boundaries
# - show units of parameters in slider, table, plots





###################################################################################


if __name__ == '__main__':

    # Create window instance
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)

    # show window
    window.show()
    sys.exit(app.exec_())