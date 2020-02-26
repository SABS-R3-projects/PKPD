from typing import List

import numpy as np
import myokit
import pandas as pd
import pints
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import patches
from PyQt5 import QtCore, QtWidgets

from PKPD.gui.utils import slider as sl
from PKPD.inference import inference as inf
from PKPD.model import model as m


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
        self.patient_ids = [1]  # default: just a single patient
        self.dose_schedule = None
        self.boundaries_are_on = True

        # initialising the figure
        self.data_model_figure = Figure()
        self.data_model_figure_view = FigureCanvas(self.data_model_figure)

        # set the layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.data_model_figure_view)
        layout.addLayout(self._init_interactive_group())
        self.setLayout(layout)

    def extract_data_from_dataframe(self):
        """Splits dataframe into ID, time, states and dose numpy arrays.
        """
        # get data labels
        patient_id_label, self.time_label, self.state_labels, dose_schedule_label = self._get_data_labels()

        # check dimensionality of problem for plotting and inference
        self.data_dimension = len(self.state_labels)
        self.is_single_output_model = self.data_dimension == 1

        # get patient IDs, if available
        if patient_id_label is not None:
            # get patient ID for each data point
            self.patient_ids_mask = self.main_window.home.data_df[patient_id_label].to_numpy()

            # reduce to unique IDs
            self.patient_ids = np.unique(self.patient_ids_mask)

        # if no patient IDs are available, assume that all data is from one patient and assign ID 1
        else:
            # create patient mask for compatibility with the rest of the code
            number_rows = self.main_window.home.data_df.shape[0]
            self.patient_ids_mask = np.ones(number_rows, dtype=int)

            # reduce to unique IDs
            self.patient_ids = [1]

        # get dose schedule, if available
        if dose_schedule_label is not None:
            self.raw_dose_schedule = self.main_window.home.data_df[dose_schedule_label].to_numpy()
        else:
            self.raw_dose_schedule = None

        # sort into time and state data
        self.time_data = self.main_window.home.data_df[self.time_label].to_numpy()
        if self.is_single_output_model:
            state_label = self.state_labels[0]
            self.state_data = self.main_window.home.data_df[state_label].to_numpy()
        else:
            self.state_data = self.main_window.home.data_df[self.state_labels].to_numpy()

    def _get_data_labels(self):
        """Returns the labels associated to the patient IDs, the time data, state data and dosing schedule. For non-existent labels
        `None` is returned.
        """
        # get labels in data frame
        labels = self.main_window.home.data_df.keys()

        # check whether patient IDs and/or doses are provided
        are_patient_IDs_provided = self.main_window.home.patient_id_check_box.isChecked()
        is_dosing_schedule_provided = self.main_window.home.dose_schedule_check_box.isChecked()

        # return labels according to data structure
        if are_patient_IDs_provided and is_dosing_schedule_provided:
            patient_ID_label = labels[0]
            time_label = labels[1]
            state_labels = labels[2:-1]
            dose_label = labels[-1]

            return patient_ID_label, time_label, state_labels, dose_label
        elif are_patient_IDs_provided and not is_dosing_schedule_provided:
            patient_ID_label = labels[0]
            time_label = labels[1]
            state_labels = labels[2:]
            dose_label = None

            return patient_ID_label, time_label, state_labels, dose_label
        elif not are_patient_IDs_provided and is_dosing_schedule_provided:
            patient_ID_label = None
            time_label = labels[0]
            state_labels = labels[1:-1]
            dose_label = labels[-1]

            return patient_ID_label, time_label, state_labels, dose_label
        else:
            patient_ID_label = None
            time_label = labels[0]
            state_labels = labels[1:]
            dose_label = None

            return patient_ID_label, time_label, state_labels, dose_label

    def get_dose_schedule(self):
        """Get dose schedule from data, if provided.
        """
        # if no dose schedule is provided, set dose schedule to None for each patient
        if self.raw_dose_schedule is None:
            self.dose_schedule = [None] * len(self.patient_ids)

        # if dose schedule is provided, extract protocols for patients
        else:
            # initialise dose container
            self.dose_schedule = []
            for patient_id in self.patient_ids:
                # create patient mask
                patient_mask = self.patient_ids_mask == patient_id

                # get dose data
                raw_time_data = self.time_data[patient_mask]
                raw_dose_data = self.raw_dose_schedule[patient_mask]

                # crate NaN mask
                nan_mask =~ np.isnan(raw_dose_data)

                # filter nans
                time_data, dose_data = raw_time_data[nan_mask], raw_dose_data[nan_mask]

                # save extracted schedule in container
                if not dose_data:
                    # if dose data is empty, fill cotainer with None
                    self.dose_schedule.append(None)
                else:
                    # set duration of doses (arbitrary) TODO: come up with better solution
                    number_of_doses = len(dose_data)
                    duration_data = np.ones(number_of_doses)

                    # if dose data not empty, fill container with data
                    self.dose_schedule.append([time_data, dose_data, duration_data])


    def filter_data(self):
        """Filter time and state data from rows for which the state only contains NaNs.
        """
        # if single output problem, remove all entries where state is NaN
        if self.is_single_output_model:
            # create NaN mask
            mask =~ np.isnan(self.state_data)

            # time and state data for non-NaN values
            self.time_data = self.time_data[mask]
            self.state_data = self.state_data[mask]

            # update patient IDs mask and patient IDs
            self.patient_ids_mask = self.patient_ids_mask[mask]
            self.patient_ids = np.unique(self.patient_ids_mask)

        # if multi output problem, remove only those rows where all state entries are NaN
        else:
            # create NaN mask
            mask2d =~ np.isnan(self.state_data)
            mask = np.all(mask2d, axis=1)

            # mask patient_id_mask, time and state data for non-NaN values
            self.time_data = self.time_data[mask]
            self.state_data = self.state_data[mask, :]

            # update patient IDs mask and patient IDs
            self.patient_ids_mask = self.patient_ids_mask[mask]
            self.patient_ids = np.unique(self.patient_ids_mask)


    def update_dose_schedule(self, schedule:List) -> None:
        """Update dose schedule.

        Arguments:
            schedule {List} -- Schedule of all dose events [dose amount, time, duration] of a patient.
        """
        # if dose schedule is None, keep protocol from .mmt file
        if schedule is None:
            pass

        # if dose schedule exist, create protocol and add dosing events to it
        else:
            # get time and dose data
            time_data, dose_data, duration_data = schedule

            # create protocol object
            protocol = myokit.Protocol()

            # add dose events to protocol
            for dose_id, dose_amount in enumerate(dose_data):
                # compute dosing level
                level = dose_amount / duration_data[dose_id]

                # schedule dosing event
                protocol.schedule(level=level, start=time_data[dose_id], duration=duration_data[dose_id])

            # update dose schedule
            self.main_window.model.simulation.set_protocol(protocol)


    def add_data_to_data_model_plot(self):
        """Adds the data from the in the home tab chosen data file to the previously initialised figure. For multi-
        dimensional data, the figure is split into subplots.
        """
        if self.is_single_output_model: # single output
            # clear figure
            self.data_model_figure.clf()

            # get state label
            state_label = self.state_labels[0]

            # create plot
            self.data_model_ax = self.data_model_figure.subplots()
            for patient_id in self.patient_ids:
                # create mask for patient specific data
                mask = self.patient_ids_mask == patient_id

                # create scatter plot
                self.data_model_ax.scatter(x=self.time_data[mask], y=self.state_data[mask], marker='o', edgecolor='black',
                                            alpha=0.5)

                # add x, y labels
                self.data_model_ax.set_xlabel(self.time_label)
                self.data_model_ax.set_ylabel(state_label)

            # add data label to legend (hack)
            self.data_model_ax.scatter(x=[], y=[], marker='o', color='darkgrey', edgecolor='black', alpha=0.5, label='data')
            self.data_model_ax.legend()

        else: # multi output
            # clear figure
            self.data_model_figure.clf()

            # create subplots for each compartment
            self.data_model_ax = self.data_model_figure.subplots(nrows=self.data_dimension, sharex=True)

            # create subplots for each measured compartment
            for dim in range(self.data_dimension):

                # color data by patient ID
                for patient_id in self.patient_ids:
                    # create mask for patient specific data
                    mask = self.patient_ids_mask == patient_id

                    # create scatter plot
                    self.data_model_ax[dim].scatter(x=self.time_data[mask], y=self.state_data[mask, dim], marker='o',
                                                    edgecolor='black', alpha=0.5)

                    # add ylabel for compartment
                    self.data_model_ax[dim].set_ylabel(self.state_labels[dim])

                # add legend to compartment subplot (hack)
                self.data_model_ax[dim].scatter(x=[], y=[], marker='o', color='darkgrey', edgecolor='black', alpha=0.5, label='data')
                self.data_model_ax[dim].legend()

            # add xlabel to the bottom of the vertically stacked subplots
            self.data_model_ax[-1].set_xlabel(self.time_label)

        # refresh canvas
        self.data_model_figure_view.draw()


    def _init_interactive_group(self):
        """Initialises the dose schedule interface, functional sliders and buttons of the simulation tab.

        Returns:
            v_box {QVBoxLayout} -- Returns the layout arranging the sliders, buttons and the inferred parameter table.
        """
        # initialise dose interface, sliders, 'plot model' button,'infer model' button and inferred parameters table
        dose_schedule_group = self._initialise_dose_schedule_group()
        slider_group = self._initialise_slider_group()
        plot_buttons = self._initialise_plot_buttons()
        infer_buttons = self._initialise_infer_buttons()
        self.inferred_parameter_table = QtWidgets.QTableWidget()

        # arrange widgets vertically
        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(slider_group)
        v_box.addLayout(plot_buttons)
        v_box.addLayout(infer_buttons)
        v_box.addWidget(self.inferred_parameter_table)

        return v_box

    def _initialise_dose_schedule_group(self):
        pass


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
        self._create_plot_option_window()

        # arrange button horizontally
        h_box = QtWidgets.QHBoxLayout()
        h_box.addWidget(plot_button)
        h_box.addWidget(option_button)

        return h_box

    def _initialise_infer_buttons(self):
        # create plot model button
        infer_button = QtWidgets.QPushButton('infer model')
        infer_button.clicked.connect(self.on_infer_model_click)

        # create option button
        option_button = QtWidgets.QPushButton('option')
        option_button.clicked.connect(self.on_infer_option_click)

        # create option window
        self._create_infer_option_window()

        # arrange button horizontally
        h_box = QtWidgets.QHBoxLayout()
        h_box.addWidget(infer_button)
        h_box.addWidget(option_button)

        return h_box

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
        boundary_toggle = self._create_boundary_toggle()

        # create apply / cancel buttons
        apply_cancel_buttons = self._create_apply_cancel_buttons()

        # arrange options vertically
        v_box = QtWidgets.QVBoxLayout()
        v_box.addLayout(optimiser_options)
        v_box.addLayout(objective_function_options)
        v_box.addLayout(boundary_toggle)
        v_box.addLayout(apply_cancel_buttons)

        # add options to window
        self.infer_option_window.setLayout(v_box)

    def _create_optimiser_options(self):
        """Creates a dropdown menu to select an optimiser method for the inference.

        Returns:
            h_box {QHBoxLayout} -- Returns label and dropdown menu.
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

        # arrange label and dropdown menu horizontally
        h_box = QtWidgets.QHBoxLayout()
        h_box.addWidget(label)
        h_box.addWidget(self.optimiser_dropdown_menu)

        return h_box

    def _create_objective_function_options(self):
        """Creates a dropdown menu to select an error measure for the inference.

        Returns:
            h_box {QHBoxLayout} -- Returns label and dropdown menu.
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

        # arrange label and dropdown menu horizontally
        h_box = QtWidgets.QHBoxLayout()
        h_box.addWidget(label)
        h_box.addWidget(self.error_measure_dropdown_menu)

        return h_box

    def _create_boundary_toggle(self):
        """Creates a checkbox used to set boundary checks. Defaults to checked (True).

        Returns:
            h_box {QHBoxLayout} -- Layout containing checkbox.
        """

        label = QtWidgets.QLabel('turn on boundary checking:')
        self.boundary_toggle = QtWidgets.QCheckBox()

        h_box = QtWidgets.QHBoxLayout()
        h_box.addWidget(label)
        h_box.addWidget(self.boundary_toggle)
        self.boundary_toggle.setChecked(True)

        return h_box

    def _create_apply_cancel_buttons(self):
        """Creates an apply and cancel button to either update the inference settings or
        closing the option window without updating.

        Returns:
            h_box {QHBoxLayout} -- Returns layout arranging the apply and cancel button.
        """
        # create apply and cancel button
        apply_button = QtWidgets.QPushButton('apply')
        apply_button.clicked.connect(self.on_infer_option_apply_click)
        cancel_button = QtWidgets.QPushButton('cancel')
        cancel_button.clicked.connect(self.on_infer_option_cancel_button_click)

        # arrange buttons horizontally
        h_box = QtWidgets.QHBoxLayout()
        h_box.addStretch(1)
        h_box.addWidget(apply_button)
        h_box.addWidget(cancel_button)

        return h_box

    def _plot_options_apply_cancel_buttons(self):
        """Creates an apply and cancel button to either update the inference settings or
        closing the option window without updating.

        Returns:
            h_box {QHBoxLayout} -- Returns layout arranging the apply and cancel button.
        """
        # create apply and cancel button
        apply_button = QtWidgets.QPushButton('apply')
        apply_button.clicked.connect(self.on_plot_option_apply_click)
        cancel_button = QtWidgets.QPushButton('cancel')
        cancel_button.clicked.connect(self.on_plot_option_cancel_click)

        # arrange buttons horizontally
        h_box = QtWidgets.QHBoxLayout()
        h_box.addStretch(1)
        h_box.addWidget(apply_button)
        h_box.addWidget(cancel_button)

        return h_box

    @QtCore.pyqtSlot()
    def on_infer_option_apply_click(self):
        """Reaction to left-clicking the infer option 'apply' button. Updates the inference settings
        and closes the option window.
        """
        # update infer options
        self._set_optimiser()
        self._set_error_measure()
        self._set_boundary_check()

        # close option window
        self.infer_option_window.close()

    @QtCore.pyqtSlot()
    def on_plot_option_apply_click(self):
        """Reaction to left-clicking the infer option 'apply' button. Updates the inference settings
        and closes the option window.
        """
        # update plot options
        self._change_y_axis_scaling()

        # close option window
        self.plot_option_window.close()

    def _change_y_axis_scaling(self):

        scale = self.y_axis_dropdown_menu.currentText()
        try:
            self.data_model_ax.set_yscale(scale)
        except:
            for elem in range(self.data_dimension):
                self.data_model_ax[elem].set_yscale(scale)
        self.data_model_figure_view.draw() #refresh canvas

    def on_plot_option_cancel_click(self):
        """Reaction to left-clicking the infer option 'cancel' button. Closes the window.
        """
        # close option window
        self.plot_option_window.close()

    def _set_optimiser(self):
        # TODO: Nelder-Mead does not support boundaries. So should be cross-linked with turning boundaries off.
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

    def _set_boundary_check(self):
        """Sets boundaries_are_on to True if the checkbox is checked when apply is clicked (False if not checked).
        """
        self.boundaries_are_on = self.boundary_toggle.isChecked()

    @QtCore.pyqtSlot()
    def on_infer_option_cancel_button_click(self):
        """Reaction to left-clicking the infer option 'cancel' button. Closes the window.
        """
        # close option window
        self.infer_option_window.close()

    def _create_plot_option_window(self):
        """Creates an option window to set the plotting settings.
        """
        # create option window
        self.plot_option_window = QtWidgets.QDialog()
        self.plot_option_window.setWindowTitle('Plotting options')

        # define dropdown dimension
        self.dropdown_menu_width = 190 # to match inference option window

        # create plotting options
        y_axis_options = self._create_y_axis_options()

        # create apply / cancel buttons
        apply_cancel_buttons = self._plot_options_apply_cancel_buttons()

        # vertical layout
        v_box = QtWidgets.QVBoxLayout()
        v_box.addLayout(y_axis_options)
        v_box.addLayout(apply_cancel_buttons)

        # add options to window
        self.plot_option_window.setLayout(v_box)

    def _create_y_axis_options(self):
        # create label
        label = QtWidgets.QLabel('y axis scaling:')

        # define options
        axis_types = ['linear', 'log']

        # create dropdown menu for options
        self.y_axis_dropdown_menu = QtWidgets.QComboBox()
        self.y_axis_dropdown_menu.setMinimumWidth(self.dropdown_menu_width)
        for scale in axis_types:
            self.y_axis_dropdown_menu.addItem(scale)

        # arrange label and dropdown menu horizontally
        h_box = QtWidgets.QHBoxLayout()
        h_box.addWidget(label)
        h_box.addWidget(self.y_axis_dropdown_menu)

        return h_box

    def fill_parameter_slider_group(self):
        """Fills the initialised slider group with parameter sliders (the number of sliders is determined by the
        number of parameters in the model).
        """
        self._clear_slider_group()

        # get parameter names
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
            # setting an items parent to None deletes it, according to Stack Overflow
            self.parameter_sliders.itemAtPosition(item_id, 0).widget().setParent(None)

    def _create_slider(self, parameter_name: str):
        """Creates slider group. Includes parameter label, value slider, value text field and labels for slider boundaries.

        Arguments:
            parameter_name {str} -- Parameter name for which the slider is created.
        
        Returns:
            slider_box {QGroupBox} -- Returns a widget containing labels, a value slider and a value text field for the parameter.
        """
        # initialise widget
        slider_box = QtWidgets.QGroupBox(self._give_param_label(parameter_name))

        # create horizontal slider
        slider = sl.DoubleSlider()
        slider.setMinimum(0.1) # arbitrary choice
        slider.setValue(1) # default arbitrary, but it seems reasonable to avoid zero
        slider.setMaximum(30) # arbitrary choice
        slider.setTickPosition(sl.DoubleSlider.TicksBothSides)

        # keep track of sliders
        self.slider_container.append(slider)

        # create labels
        min_current_max_value = self._create_min_current_max_value_label(slider)
        slider.valueChanged[int].connect(self._update_parameter_values)

        # arrange slider and labels
        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(slider)
        v_box.addLayout(min_current_max_value)
        v_box.addStretch(1)
        slider_box.setLayout(v_box)

        return slider_box

    def _give_param_label(self, parameter_name):
        """Takes a parameter name and returns a string with the parameter label (if exists), name (if no label),
        and units.

        Arguments: parameter_name -- name of myokit parameter (string)

        Returns: slider_label -- appropriate parameter name (string)
        """
        var = self.main_window.model.model.get(parameter_name)
        unit = var.unit()
        parameter_label = var.label()

        # If there's a label or units, add them to the naming string.
        if parameter_label is not None:
            if unit is not None:
                slider_label = str(parameter_label + ' ' + str(unit))
            else:
                slider_label = str(parameter_label)
        else:
            if unit is not None:
                slider_label = str(parameter_name + ' ' + str(unit))
            else:
                slider_label = str(parameter_name)

        return slider_label

    def _create_min_current_max_value_label(self, slider:QtWidgets.QSlider):
        """Creates labels for a slider displaying the current position of the slider and the minimum and
        maximum value of the slider.

        Arguments:
            slider {QtWidgets.QSlider} -- Parameter slider.
        
        Returns:
            h_box {QHBoxLayout} -- Returns a layout arranging the slider labels.
        """
        # create min/max labels and text field for current value
        min_value = QtWidgets.QLabel('%.1f' % slider.minimum())
        text_field = QtWidgets.QLineEdit('%.1f' % slider.value())
        max_value = QtWidgets.QLabel('%.1f' % slider.maximum())

        # keep track of parameter values and min/max labels
        self.parameter_text_field_container.append(text_field)
        self.slider_min_max_label_container.append([min_value, max_value])

        # arrange widgets horizontally
        h_box = QtWidgets.QHBoxLayout()
        h_box.addWidget(min_value)
        h_box.addStretch(1)
        h_box.addWidget(text_field)
        h_box.addStretch(1)
        h_box.addWidget(max_value)

        return h_box

    def _update_parameter_values(self):
        """Updates parameter text fields when slider position is moved and updates the model plot in the
        figure, should live plotting be enabled.
        """
        # update slider text fields
        for slider_id, slider in enumerate(self.slider_container):
            self.parameter_values[slider_id] = round(number=slider.value(), ndigits=1)
            self.parameter_text_field_container[slider_id].setText('%.1f' % self.parameter_values[slider_id])

        # plot model if live plotting is enabled
        if self.enable_live_plotting and self.is_single_output_model:
            self._plot_single_output_model()
        elif self.enable_live_plotting and not self.is_single_output_model:
            self._plot_multi_output_model()

    def fill_plot_option_window(self):
        #  TODO: finish this!
        # create text fields
        for slider in self.slider_container:
            pass

    def fill_infer_option_window(self):
        #  TODO: finish this!
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

        # enable removal of plots to prevent flooding of figure
        self.enable_line_removal = True

    def _plot_single_output_model(self):
        """Plots the model in dashed, grey lines.
        """
        # solve forward problem for current parameter set
        self.state_values = self.main_window.model.simulate(parameters=self.parameter_values,
                                                            times=self.times
                                                            )

        # remove previous graph to avoid flooding the figure
        if self.enable_line_removal:
            self.data_model_ax.lines.pop()

        # plot model
        self.data_model_ax.plot(self.times, self.state_values, linestyle='dashed', color='grey')

        # refresh canvas
        self.data_model_figure_view.draw()

    def _plot_multi_output_model(self):
        """Plots the model in dashed, grey lines. Each state dimension is plotted to a separate subplot.
        """
        # solve forward problem for current parameter set
        self.state_values = self.main_window.model.simulate(parameters=self.parameter_values,
                                                            times=self.times
                                                            )

        # remove previous graphs from subplots to avoid flooding the figure
        if self.enable_line_removal:
            for dim in range(self.data_dimension):
                self.data_model_ax[dim].lines.pop()

        # plot model
        for dim in range(self.data_dimension):
            self.data_model_ax[dim].plot(self.times, self.state_values[:, dim], linestyle='dashed', color='grey')

        # refresh canvas
        self.data_model_figure_view.draw()

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
        initial_parameters = np.empty(len(self.parameter_values))
        for parameter_id, parameter_text_field in enumerate(self.parameter_text_field_container):
            value = float(parameter_text_field.text())
            initial_parameters[parameter_id] = value # Note: order of text fields matches order of params in inverse problem class

        # set parameter boundaries
        self._set_parameter_boundaries(initial_parameters)

        # if initial parameters lie within provided boundaries, start inference
        if self.correct_initial_values:
            try:
                # find parameters
                self.main_window.problem.find_optimal_parameter(initial_parameter=initial_parameters)
                self.estimated_parameters = self.main_window.problem.estimated_parameters

                # plot infered model
                self._plot_inferred_model()

                # update slider position to infered parameters
                self._update_sliders_to_inferred_params()

                # update parameter table
                self._update_parameter_table()
            except ArithmeticError:
                # generate error message
                error_message = str('Convergence test failures occurred too many times during one internal time step or minimum' +
                                ' step size was reached. Please try different inference settings!')
                QtWidgets.QMessageBox.question(self, 'Convergence error!', error_message, QtWidgets.QMessageBox.Yes)
            except myokit.SimulationError:
                # generate error message
                error_message = str('A numerical error occurred during the simulation likely due to unsuitable inference settings.' +
                                ' Please try different inference settings!')
                QtWidgets.QMessageBox.question(self, 'Numerical error!', error_message, QtWidgets.QMessageBox.Yes)

    def _set_parameter_boundaries(self, initial_parameters:np.ndarray):
        """Gets slider boundaries and restricts the parameter search to those intervals. If initial parameters lie outside the domain of
        support, an error message is returned.

        Arguments:
            initial_parameters {np.ndarray} -- Initial point in parameter space for the inference.
        """
        # tolerance extension of boundaries (as values can be set to slider boundaries)
        increment = 1.0E-7

        # if boundaries are turned off, send None to optimiser
        if self.boundaries_are_on is False:
            self.main_window.problem.set_parameter_boundaries(None)
            self.correct_initial_values = True

        # if boundaries are turned on, get from sliders
        elif self.boundaries_are_on is True:
            # get boundaries from sliders
            min_values = []
            max_values = []

            for param_id, slider in enumerate(self.slider_container):
                minimum = slider.minimum() - increment # extend boundaries for stability
                maximum = slider.maximum() + increment
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
                    min_values.append(minimum)
                    max_values.append(maximum)

            # set boundaries for inference
            if self.correct_initial_values:
                self.main_window.problem.set_parameter_boundaries([min_values, max_values])

    def _plot_inferred_model(self):
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
            for dim in range(self.data_dimension):
                lines = self.data_model_ax[dim].lines
                while lines:
                    lines.pop()

            # plot model
            for dim in range(self.data_dimension):
                self.data_model_ax[dim].plot(times, state_values[:, dim], color='black', label='model')
                self.data_model_ax[dim].legend()

        # refresh canvas
        self.data_model_figure_view.draw()

    def _update_sliders_to_inferred_params(self):
        """Set slider positions and text fields to inferred parameters.
        """
        for param_id, param_value in enumerate(self.estimated_parameters):
            # get slider
            slider = self.slider_container[param_id]

            # round parameter value to appropriate precision
            rounded_value = round(number=param_value, ndigits=1)

            # set slider value
            slider.setValue(rounded_value)

            # get text field
            text_field = self.parameter_text_field_container[param_id]

            # set text field value
            text_field.setText('%.1f' % rounded_value)

    def _update_parameter_table(self):
        """Fills parameter table cells with inferred parameter values.
        """
        for param_id, param_value in enumerate(self.estimated_parameters):
            # round value to 3 digits (arbitrary)
            rounded_value = round(number=param_value, ndigits=3)

            # update cell in table
            self.inferred_parameter_table.item(0, param_id).setText('%.3f' % rounded_value)
