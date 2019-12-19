import myokit
import numpy as np

from PKPD.model.abstractModel import AbstractModel

### TODO for tomorrow:
    # 1. test Model class
    # 2. time performance (possible that there is no improvement, since single call)
    # 3. connect this to inference class and see whether it works faster now
    # 4. write abstractMode class
    # 5. document everything
    # 6. move on to MCMC sampling


class Model(AbstractModel):
    """Model class inheriting from pints.ForwardModel. To solve the forward problem methods from the
    myokit package are employed.
    """
    def __init__(self, mmtfile:str) -> None:
        """Initialises the model class.

        Arguments:
            mmtfile {str} -- Path to the mmtfile defining the model and the protocol.
        """
        model, protocol, _ = myokit.load(mmtfile)
        self.state_dimension = len(model.state())
        if self.state_dimension > 1:
            raise NotImplementedError('Currently only one dimensional states are suported.')
        self.state_names = [next(model.states()).qname() for _ in range(self.state_dimension)]
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
        result = self.simulation.run(duration=times[-1]+1, log=self.state_names, log_times = times)

        return np.array(result)

    def _set_parameters(self, parameters:np.ndarray) -> None:
        """Internal helper method to set the parameters of the forward model.

        Arguments:
            parameters {np.ndarray} -- Parameters of the model. By convention [initial conditions, model parameters].
        """
        self.simulation.set_state(parameters[:self.state_dimension])
        for param_id, value in enumerate(parameters[self.state_dimension:]):
            self.simulation.set_constant(self.parameter_names[param_id], value)

