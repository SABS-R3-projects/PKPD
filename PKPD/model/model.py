import myokit
import numpy as np

from PKPD.model.abstractModel import AbstractModel


class Model(AbstractModel):
    def __init__(self, mmtfile):
        model, protocol, _ = myokit.load(mmtfile)
        self.state_names = [next(state).qname() for state in model.states()]
        self.state_dimension = len(model.state())
        if self.state_dimension > 1:
            raise NotImplementedError('Currently only one dimensional states are suported.')
        # TODO: automate name 'param'
        self.parameter_names = sorted([var.qname() for var in model.get('param').variables()])
        self.number_model_parameters = len(self.parameter_names)
        self.number_parameters_to_fit = self.state_dimension + self.number_model_parameters
        self.simulation = myokit.Simulation(model, protocol)

    def n_parameters(self):
        return self.number_parameters_to_fit

    def n_outputs(self):
        return 1

    def simulate(self, parameters, times):
        """Description follows. BUT parameter convertion: [initial value, parameter]

        Arguments:
            parameters {[type]} -- [description]
            times {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        self.simulation.reset()
        self._set_parameters(parameters)

        # duration is the last time point plus an increment to iclude the last time step.
        result = self.simulation.run(duration=times[-1]+1, log=[self.state_names], log_times = times)

        return np.array(result)

    def _set_parameters(self, parameters):
        self.simulation.set_state(parameters[:self.state_dimension])
        for param_id, value in enumerate(parameters[self.state_dimension:]):
            self.simulation.set_constant(self.parameter_names[param_id], value)

