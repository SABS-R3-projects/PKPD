import os
import sys
import myokit
from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets

from PKPD.inference import inference as inf
from PKPD.gui import abstractGui, home, simulation
from PKPD.model import model as m


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

        # show our animation
        self._show_animated_logo()

        # Timer to stop the animation
        self.anitimer = QtCore.QTimer()
        self.anitimer.setInterval(1950)
        self.anitimer.setSingleShot(True)
        self.anitimer.start()

        # fill the window with content when timer runs out.
        self.anitimer.timeout.connect(self._arrange_window_content)

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
        if self.centralWidget().movie() is not None:
            self.centralWidget().movie().stop()

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
        self.simulation = simulation.SimulationTab(self)

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

    def _create_PKPD_animation(self):
        """Shows the PKPD animation.

        Returns:
            {QLabel} -- Returns the PKPD Logo Animation.
        """
        label = QtWidgets.QLabel(self)
        animation = QtGui.QMovie('images/LOGO_Animated.gif')
        label.setMovie(animation)

        return label

    def next_tab(self):
        """Switches to the simulation tab, when triggered by clicking the 'next' QPushButton on the home tab.
        """
        if self.home.is_model_file_valid and self.home.is_data_file_valid:
            try:
                # piece dataframe into ID, time, states and dose data
                self.simulation.extract_data_from_dataframe()

                # get dose schedule TODO: write test
                self.simulation.get_dose_schedule()

                # filter data from time points with no information TODO: write test
                self.simulation.filter_data()

                # TODO: move data extraction from ploting
                # add plot of dosing schedule
                # add dose schedule option button
                # list doses of patient, if available
                # allow for adding of doses

                # plot data in simulation tab
                self.simulation.add_data_to_data_model_plot()

                # disable live plotting and line removal for the simulation
                self.simulation.enable_live_plotting = False
                self.simulation.enable_line_removal = False

                # instantiate model
                if self.simulation.is_single_output_model: # single output
                    self.model = m.SingleOutputModel(self.home.model_file)
                else: # multi output
                    self.model = m.MultiOutputModel(self.home.model_file)

                    # set model output dimension to data dimension
                    self.model.set_output_dimension(self.simulation.data_dimension)

                # fill sliders, plot options and parameter table with parameters in model
                self.simulation.fill_parameter_slider_group()
                self.simulation.fill_plot_option_window()
                self.simulation.fill_parameter_table()

                # switch to simulation tab
                self.tabs.setCurrentIndex(self.sim_tab_index)

                # instantiate inverse problem (after switching to simulation tab to improve user experience)
                self._instantiate_inverse_problem()

            except ValueError:
                # generate error message
                error_message = 'The .csv file does not seem to be properly formatted. Please check again!'
                QtWidgets.QMessageBox.question(self, 'Data structure not compatible!', error_message, QtWidgets.QMessageBox.Yes)

            # Check Units in MMT file
            try:
                self.model.model.check_units(mode=myokit.UNIT_STRICT)
            except Exception as e: # Display Warning if Inconsistent
                warning_message = 'Warning: Units may be inconsistent'
                QtWidgets.QMessageBox.question(self, warning_message, str(e),
                                               QtWidgets.QMessageBox.Yes)
        else:
            # update file dialog icons
            if not self.home.is_model_file_valid:
                self.home.model_check_mark.setPixmap(self.rescaled_rc)
            else:
                self.home.model_check_mark.setPixmap(self.rescaled_cm)
            if not self.home.is_data_file_valid:
                self.home.data_check_mark.setPixmap(self.rescaled_rc)
            else:
                self.home.data_check_mark.setPixmap(self.rescaled_cm)

            # generate error message
            error_message = 'At least one of the files does not seem to exist or does not have the correct file format. Please check again!'
            QtWidgets.QMessageBox.question(self, 'Files not found!', error_message, QtWidgets.QMessageBox.Yes)


    def _instantiate_inverse_problem(self):
        """Instantiates inverse problem for parameter optimisation.
        """
        # create model container for patients
        self.model_container = []

        # number of patients
        number_of_patients = len(self.simulation.patient_ids)

        # update schedule for each patient model
        for patient in range(number_of_patients):
            # update dose schedule TODO: write test
            self.simulation.update_dose_schedule(schedule=self.simulation.dose_schedule[patient])

            # add model to container
            self.model_container.append(self.model)

        # instantiate inverse problem
        if self.simulation.is_single_output_model:
            # instantiate single output problem
            self.problem = inf.SingleOutputInverseProblem(models=self.model_container,
                                                          times=self.simulation.time_data,
                                                          values=self.simulation.state_data
            )

        else:
            # instantiate multi output problem
            self.problem = inf.MultiOutputInverseProblem(models=self.model_container,
                                                         times=self.simulation.time_data,
                                                         values=self.simulation.state_data
            )


    def _show_animated_logo(self):
        self.setWindowTitle(self.window_title)
        animation = self._create_PKPD_animation()
        animation.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setCentralWidget(animation)
        animation.movie().start()



if __name__ == '__main__':
    # Create window instance
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)

    # show window
    window.show()

    # # show our animation
    # window._show_animated_logo()
    #
    # # fill the window with content
    # window._arrange_window_content()

    sys.exit(app.exec_())