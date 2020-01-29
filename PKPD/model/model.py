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
        model, protocol, _ = myokit.load(mmtfile)
        state_dimension = model.count_states()
        if state_dimension > 1:
            raise NotImplementedError(
                'The output seems to be multi-dimensional. You might want to try a MultiOutputProblem instead.'
                )
        self.state_name = next(model.states()).qname()
        print(model.code(line_numbers=True))


        print(self.state_name)
        print(list(model.components()))
        for component in model.components():
            print(sorted([var.qname() for var in model.get(component).variables()]))
        # TODO:
        # - define _get_parameter_names
        # - make sure the pipeline works, where the parameters are called.
        # TODO: automate name 'param'
        # self.parameter_names = sorted([var.qname() for var in model.get('param').variables()])
        # self.number_model_parameters = len(self.parameter_names)
        self.parameter_names = self._get_parameter_names(model)
        self.number_parameters_to_fit = model.count_variables(bound=False)
        self.simulation = myokit.Simulation(model, protocol)


    def _get_parameter_names(self, model):
        parameter_names = []
        for component in model.components():
            parameter_names += sorted([var.qname() for var in model.get(component).variables()])


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
        result = self.simulation.run(duration=times[-1]+1, log=[self.state_name], log_times = times)

        return result[self.state_name]


    def _set_parameters(self, parameters:np.ndarray) -> None:
        """Internal helper method to set the parameters of the forward model.

        Arguments:
            parameters {np.ndarray} -- Parameters of the model. By convention [initial condition, model parameters].
        """
        self.simulation.set_state(parameters[:1])
        for param_id, value in enumerate(parameters[1:]):
            self.simulation.set_constant(self.parameter_names[param_id], value)


class MultiOutputModel(AbstractModel):
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

