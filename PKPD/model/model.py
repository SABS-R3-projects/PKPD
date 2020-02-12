from array import array

import myokit
import numpy as np

from PKPD.model.abstractModel import AbstractModel


class SingleOutputModel(AbstractModel):
    """Model class inheriting from pints.ForwardModel. To solve the forward problem methods from the
    myokit package are employed. The sole difference to the MultiOutputProblem is that the simulate method
    returns a 1d array instead of a 2d array.
    """
    def __init__(self, mmtfile:str) -> None:
        """Initialises the model class.

        Arguments:
            mmtfile {str} -- Path to the mmtfile defining the model and the protocol.
        """
        # load model and protocol
        model, protocol, _ = myokit.load(mmtfile)

        # get state, parameter and output names
        self.state_names = [state.qname() for state in model.states()]
        self.state_dimension = len(self.state_names)
        self.output_name = next(model.variables(inter=True)).qname() # by default drug concentration (only intermediate variable in any compartment)
        self.parameter_names = self._get_parameter_names(model)
        self.number_parameters_to_fit = model.count_variables(inter=False, bound=False)

        # instantiate the simulation
        self.simulation = myokit.Simulation(model, protocol)
        self.model = model


    def _get_parameter_names(self, model:myokit.Model):
        """Gets parameter names of the ODE model, i.e. initial conditions are excluded.

        Arguments:
            model {myokit.Model} -- A myokit model.

        Returns:
            List -- List of parameter names.
        """
        parameter_names = []
        for component in model.components(sort=True):
            parameter_names += [var.qname() for var in component.variables(state=False, inter=False, bound=False, sort=True)]

        return parameter_names


    def n_parameters(self) -> int:
        """Returns the number of parameters of the model, i.e. initial conditions and model
        parameters.

        Returns:
            int -- Number of parameters.
        """
        return self.number_parameters_to_fit


    def n_outputs(self) -> None:
        """Returns the dimension of the state variable.

        Returns:
            int -- Dimensionality of the output.
        """
        return 1


    def set_output(self, output_name):
        """Sets the output of the model.

        Arguments:
            output_name {[type]} -- [description]
        """
        self.output_name = output_name


    def simulate(self, parameters:np.ndarray, times:np.ndarray) -> array:
        """Solves the forward problem and returns the state values evaluated at the times provided.

        Arguments:
            parameters {np.ndarray} -- Parameters of the model. By convention [initial conditions, model parameters].
            times {np.ndarray} -- Times at which states will be evaluated.

        Returns:
            [array] -- State values evaluated at provided times.
        """
        self.simulation.reset()
        self._set_parameters(parameters)

        # duration is the last time point plus an increment to iclude the last time step.
        result = self.simulation.run(duration=times[-1]+1, log=[self.output_name], log_times=times)

        return result[self.output_name]


    def _set_parameters(self, parameters:np.ndarray) -> None:
        """Internal helper method to set the parameters of the forward model.

        Arguments:
            parameters {np.ndarray} -- Parameters of the model. By convention [initial condition, model parameters].
        """
        self.simulation.set_state(parameters[:self.state_dimension])
        for param_id, value in enumerate(parameters[self.state_dimension:]):
            self.simulation.set_constant(self.parameter_names[param_id], value)


class MultiOutputModel(AbstractModel):
    #TODO: refactor similar to SIngleOutput model!
    """Model class inheriting from pints.ForwardModel. To solve the forward problem methods from the
    myokit package are employed. The sole difference to the SingleOutputProblem is that the simulate method
    returns a 2d array instead of a 1d array.
    """
    def __init__(self, mmtfile:str) -> None:
        """Initialises the model class.

        Arguments:
            mmtfile {str} -- Path to the mmtfile defining the model and the protocol.
        """
        model, protocol, _ = myokit.load(mmtfile)
        self.state_dimension = model.count_states()
        if self.state_dimension == 1:
            Warning(
                'The output seems to be one-dimensional. For efficiency you might want to try a SingleOutputProblem instead.'
                )
        model_states = model.states()
        self.state_names = [next(model_states).qname() for _ in range(self.state_dimension)]
        # TODO: automate name 'param'
        self.parameter_names = sorted([var.qname() for var in model.get('param').variables()])
        self.number_model_parameters = len(self.parameter_names)
        self.number_parameters_to_fit = self.state_dimension + self.number_model_parameters
        self.simulation = myokit.Simulation(model, protocol)
        self.model = model

    def n_parameters(self) -> int:
        """Returns the number of parameters of the model, i.e. initial conditions and model
        parameters.

        Returns:
            int -- Number of parameters.
        """
        return self.number_parameters_to_fit


    def n_outputs(self) -> None:
        """Returns the dimension of the state variable.

        Returns:
            int -- Dimensionality of the output.
        """
        return self.state_dimension


    def simulate(self, parameters:np.ndarray, times:np.ndarray) -> np.ndarray:
        """Solves the forward problem and returns the state values evaluated at the times provided.

        Arguments:
            parameters {np.ndarray} -- Parameters of the model. By convention [initial conditions, model parameters].
            times {np.ndarray} -- Times at which states will be evaluated.

        Returns:
            [np.ndarray] -- State values evaluated at provided times.
        """
        self.simulation.reset()
        self._set_parameters(parameters)

        # duration is the last time point plus an increment to iclude the last time step.
        output = self.simulation.run(duration=times[-1]+1, log=self.state_names, log_times = times)

        result = []
        for state in self.state_names:
            result.append(output[state])

        return np.array(result).transpose()


    def _set_parameters(self, parameters:np.ndarray) -> None:
        """Internal helper method to set the parameters of the forward model.

        Arguments:
            parameters {np.ndarray} -- Parameters of the model. By convention [initial condition, model parameters].
        """
        self.simulation.set_state(parameters[:self.state_dimension])
        for param_id, value in enumerate(parameters[self.state_dimension:]):
            self.simulation.set_constant(self.parameter_names[param_id], value)

def set_unit_format():
    """
    Set nicer display format for some commonly used units
    """

    # Common Unit Dictionary
    common_units = {
        'mL/h': myokit.units.L * 1e-3 / myokit.units.h,
        'mL': myokit.units.L * 1e-3,
        'ng': myokit.units.g * 1e-9,
        'ng/mL': myokit.units.g * 1e-9 / (myokit.units.L * 1e-3),
        'h': myokit.units.h,
        'ng/h': myokit.units.g * 1e-9 / myokit.units.h
    }

    # Set Preferred Representation in Myokit
    for name, unit in common_units.items():
        myokit.Unit.register_preferred_representation(name, unit)

set_unit_format()

