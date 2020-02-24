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
            {QLabel} -- Returns SABS R3 logo.
        """
        label = QtWidgets.QLabel(self)
        label.setPixmap(self.rescaled_sabs)

        return label


    def next_tab(self):
        """Switches to the simulation tab, when triggered by clicking the 'next' QPushButton on the home tab.
        """
        if self.home.is_model_file_valid and self.home.is_data_file_valid:
            try:
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

                # get dose schedule
                # TODO:
                # 1. impelement this function based on non-NaN entries in dose and patient ID
                # 2. change below problem setup, by creating model list and updating their protocol
                #       - this may be best done by implementing helper function for protocol update (
                #         could be used in the GUI to manually adjust protocol)
                #       - changes in model!! Check simulation documentation.
                #       - update dose amount as multiplier, not level
                # 3. check whether inference works
                # 4. extend to multi-output problem
                # 5. write tests for added functions!!!! like filter_data etc.

                self.simulation.get_dose_schedule()

                # filter data from time points with no information
                self.simulation.filter_data()

                # instantiate inverse problem (after switching to simulation tab to improve user experience)
                if self.simulation.is_single_output_model:
                    # instantiate single output problem
                    self._instantiate_single_output_problem()

                # if multi-output problem
                else:
                    # if no patient IDs exist, initiate a single inverse problem
                    if self.simulation.patient_ids is None:
                        # create inverse problem
                        self.problem = inf.MultiOutputInverseProblem(model=self.model,
                                                                     times=self.simulation.time_data,
                                                                     values=self.simulation.state_data
                                                                     )

                    # if patient data exists, initiate patient-specific inverse problems
                    else:
                        self.problem = []
                        for patient_id in self.simulation.patient_ids:
                            # create mask for patient-specific data
                            mask = self.simulation.patient_ids_mask == patient_id

                            # create inverse problems
                            self.problem.append(inf.MultiOutputInverseProblem(model=self.model,
                                                                              times=self.simulation.time_data[mask],
                                                                              values=self.simulation.state_data[mask]
                                                                              )
                            )

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


    def _instantiate_single_output_problem(self):
        # if no patient IDs exist, initiate a single inverse problem
        if self.simulation.patient_ids is None:
            # get dose schedule
            schedule = self.simulation.dose_schedule[0]

            # update dose schedule
            self.simulation.update_dose_schedule(schedule=schedule)

            # create inverse problem
            self.problem = inf.SingleOutputInverseProblem(models=[self.model],
                                                          times=[self.simulation.time_data],
                                                          values=[self.simulation.state_data]
                                                          )

        # if patient data exists, initiate patient-specific inverse problems
        else:
            self.problem = []
            for patient_id in self.simulation.patient_ids:
                # update dose schedule
                self.simulation.update_dose_schedule(schedule=self.simulation.dose_schedule[patient_id])

                # create mask for patient-specific data
                mask = self.simulation.patient_ids_mask == patient_id

                # create inverse problems
                self.problem.append(inf.SingleOutputInverseProblem(models=self.model,
                                                                   times=self.simulation.time_data[mask],
                                                                   values=self.simulation.state_data[mask]
                                                                   )
                )


    def _instantiate_multi_output_problem(self):
        # if no patient IDs exist, initiate a single inverse problem
        if self.simulation.patient_ids is None:
            # get dose schedule
            schedule = self.simulation.dose_schedule[0]

            # update dose schedule
            self.simulation.update_dose_schedule(schedule=schedule)

            # create inverse problem
            self.problem = inf.MultiOutputInverseProblem(model=self.model,
                                                            times=self.simulation.time_data,
                                                            values=self.simulation.state_data
                                                            )

        # if patient data exists, initiate patient-specific inverse problems
        else:
            self.problem = []
            for patient_id in self.simulation.patient_ids:
                # update dose schedule
                self.simulation.update_dose_schedule(schedule=self.simulation.dose_schedule[patient_id])

                # create mask for patient-specific data
                mask = self.simulation.patient_ids_mask == patient_id

                # create inverse problems
                self.problem.append(inf.MultiOutputInverseProblem(model=self.model,
                                                                    times=self.simulation.time_data[mask],
                                                                    values=self.simulation.state_data[mask]
                                                                    )
                )


if __name__ == '__main__':
    # Create window instance
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)

    # show window
    window.show()
    sys.exit(app.exec_())