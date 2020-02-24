import numpy as np
import myokit
import pandas as pd
import pints
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets

from PKPD.gui.utils import slider as sl
from PKPD.inference import inference as inf
from PKPD.model import model as m

class CollapsibleBox(QtWidgets.QWidget):
    """
    Class to provide custom collapsible menu boxes in PyQt5
    """
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QtWidgets.QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        self.content_area = QtWidgets.QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.content_area.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

        self.manual_state = False

    @QtCore.pyqtSlot()
    def on_pressed(self):
        checked = self.manual_state
        #print('Initial State: ', checked)
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
        )
        #print('After Setting Arrow Type', self.toggle_button.isChecked())
        self.toggle_animation.setDirection(QtCore.QAbstractAnimation.Forward if not checked else QtCore.QAbstractAnimation.Backward)
        self.toggle_animation.start()
        #print('After Animation: ', self.toggle_button.isChecked())

        #self.toggle_button.toggle()
        self.manual_state = not checked

    def setContentLayout(self, layout):
        duration = 10
        self.content_area.setLayout(layout)
        collapsed_height = (
            self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(duration)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)




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
        self.boundaries_are_on = True

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
        # get data labels
        patient_id_label, time_label, state_labels, dose_schedule_label = self._get_data_labels()

        # check dimensionality of problem for plotting and inference
        self.data_dimension = len(state_labels)
        self.is_single_output_model = self.data_dimension == 1

        # sort into time and state data
        self.time_data = self.main_window.home.data_df[time_label].to_numpy()
        if self.is_single_output_model:
            state_label = state_labels[0]
            self.state_data = self.main_window.home.data_df[state_label].to_numpy()
        else:
            self.state_data = self.main_window.home.data_df[state_labels].to_numpy()

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
            self.data_model_ax = self.data_model_figure.subplots(nrows=self.data_dimension, sharex=True)
            for dim in range(self.data_dimension):
                self.data_model_ax[dim].scatter(x=self.time_data, y=self.state_data[:, dim], label='data', marker='o',
                                                color='darkgreen', edgecolor='black', alpha=0.5)
                self.data_model_ax[dim].set_ylabel(state_labels[dim])
                self.data_model_ax[dim].legend()
            self.data_model_ax[-1].set_xlabel(time_label)

            # refresh canvas
            self.canvas.draw()


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
        self.parameter_sliders = QtWidgets.QGridLayout() #QtWidgets.QVBoxLayout()#

        # add grid layout to slider group
        slider_group.setLayout(self.parameter_sliders)

        # make slider group scrollable, such that window is never exceeded
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(slider_group)
        scroll.setWidgetResizable(True)

        # fix vertical space that sliders can take up
        height = 0.7 * self.main_window.height
        scroll.setFixedHeight(height)
        #layout.setAlignment(info, Qt.AlignTop)

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

        # arrange button horizontally
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
        boundary_toggle = self._create_boundary_toggle()

        # create apply / cancel buttons
        apply_cancel_buttons = self._create_apply_cancel_buttons()

        # arrange options vertically
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(optimiser_options)
        vbox.addLayout(objective_function_options)
        vbox.addLayout(boundary_toggle)
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

        # arrange label and dropdown menu horizontally
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

        # arrange label and dropdown menu horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.error_measure_dropdown_menu)

        return hbox


    def _create_boundary_toggle(self):
        """Creates a checkbox used to set boundary checks. Defaults to checked (True).

        Returns:
            hbox {QHBoxLayout} -- Layout containing checkbox.
        """

        label = QtWidgets.QLabel('turn on boundary checking:')
        self.boundarytoggle = QtWidgets.QCheckBox()

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.boundarytoggle)
        self.boundarytoggle.setChecked(True)

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

        # arrange buttons horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(apply_button)
        hbox.addWidget(cancel_button)

        return hbox


    def _plot_options_apply_cancel_buttons(self):
        """Creates an apply and cancel button to either update the inference settings or
        closing the option window without updating.

        Returns:
            hbox {QHBoxLayout} -- Returns layout aranging the apply and cancel button.
        """
        # create apply and cancel button
        apply_button = QtWidgets.QPushButton('apply')
        apply_button.clicked.connect(self.on_plot_option_apply_click)
        cancel_button = QtWidgets.QPushButton('cancel')
        cancel_button.clicked.connect(self.on_plot_option_cancel_click)

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
        self._set_boundary_check()

        # close option window
        self.infer_option_window.close()


    @QtCore.pyqtSlot()
    def on_plot_option_apply_click(self):
        """Reaction to left-clicking the infer option 'apply' button. Updates the inference settings
        and closes the option window.
        """
        # update plot options
        self._change_yaxis_scaling()

        # close option window
        self.plot_option_window.close()


    def _change_yaxis_scaling(self):

        scale = self.yaxis_dropdown_menu.currentText()
        try:
            self.data_model_ax.set_yscale(scale)
        except:
            for elem in range(self.data_dimension):
                self.data_model_ax[elem].set_yscale(scale)
        self.canvas.draw() #refresh canvas


    def on_plot_option_cancel_click(self):
        """Reaction to left-clicking the infer option 'cancel' button. Closes the window.
        """
        # close option window
        self.plot_option_window.close()


    def _set_optimiser(self):
        # TODO: Nelder-Mead does not support boundaries. So should be cross-linked with tunring boundaries off.
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
        self.boundaries_are_on = self.boundarytoggle.isChecked()


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
        yaxis_options = self._create_yaxis_options()

        # create apply / cancel buttons
        apply_cancel_buttons = self._plot_options_apply_cancel_buttons()

        # vertical layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(yaxis_options)
        vbox.addLayout(apply_cancel_buttons)

        # add options to window
        self.plot_option_window.setLayout(vbox)


    def _create_yaxis_options(self):
        # create label
        label = QtWidgets.QLabel('y axis scaling:')

        # define options
        axis_types = ['linear', 'log']

        # create dropdown menu for options
        self.yaxis_dropdown_menu = QtWidgets.QComboBox()
        self.yaxis_dropdown_menu.setMinimumWidth(self.dropdown_menu_width)
        for scale in axis_types:
            self.yaxis_dropdown_menu.addItem(scale)

        # arange label and dropdown menu horizontally
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(self.yaxis_dropdown_menu)

        return hbox


    def fill_parameter_slider_group(self):
        """Fills the initialised slider group with parameter sliders (the number of sliders is determined by the
        number of parameters in the model).
        """
        self._clear_slider_group()

        # get parameter names
        state_names = self.main_window.model.state_names
        model_param_names = self.main_window.model.parameter_names # parameters except initial conditions
        print(model_param_names)
        print(state_names)
        parameter_names = state_names + model_param_names # parameters including initial conditions
        #param

        # fill up grid with slider objects
        self.slider_container = [] # store in list to be able to update later
        self.slider_min_max_label_container = [] # store in list to be able to update later
        self.parameter_text_field_container = [] # store in list to be able to update later


        # Get unique list of components as a set
        collapse_boxes = set([p.split('.')[0] for p in parameter_names])

        # Create box for each component:
        for name in collapse_boxes:
            box = CollapsibleBox("{}".format(name))
            self.parameter_sliders.addWidget(box) #add to parameter slider section
            lay = QtWidgets.QGridLayout()
            # Add correct parameters to each box component
            # But keeping original ID labelling so as not to affect inference etc.
            for param_id, param_name in enumerate(parameter_names):
                if param_name.split('.')[0] == name:
                    lay.addWidget(self._create_slider(param_name), param_id, 0)
            box.setContentLayout(lay)
            #self.parameter_sliders.addStretch()
            self.parameter_sliders.setAlignment(QtCore.Qt.AlignTop)



        # initialise container to store parameter values (for efficiency)
        number_parameters = len(self.parameter_text_field_container)
        self.parameter_values = np.empty(number_parameters)


    def _clear_slider_group(self):
        """Clears the slider group from pre-existing sliders.
        """
        number_items_in_group = self.parameter_sliders.count()
        for item_id in range(number_items_in_group):
            print(item_id)
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
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(slider)
        vbox.addLayout(min_current_max_value)
        vbox.addStretch(1)
        slider_box.setLayout(vbox)

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
            hbox {QHBoxLayout} -- Returns a layout arranging the slider labels.
        """
        # create min/max labels and text field for current value
        min_value = QtWidgets.QLabel('%.1f' % slider.minimum())
        text_field = QtWidgets.QLineEdit('%.1f' % slider.value())
        max_value = QtWidgets.QLabel('%.1f' % slider.maximum())

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
            for dim in range(self.data_dimension):
                self.data_model_ax[dim].lines.pop()

        # plot model
        for dim in range(self.data_dimension):
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
                self._plot_infered_model()

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
        # tolerance extenstion of boundaries (as values can be set to slider boundaries)
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
                print(minimum, initial_value, maximum)

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
            for dim in range(self.data_dimension):
                lines = self.data_model_ax[dim].lines
                while lines:
                    lines.pop()

            # plot model
            for dim in range(self.data_dimension):
                self.data_model_ax[dim].plot(times, state_values[:, dim], color='black', label='model')
                self.data_model_ax[dim].legend()

        # refresh canvas
        self.canvas.draw()


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