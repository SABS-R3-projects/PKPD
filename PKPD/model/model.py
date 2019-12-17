from PKPD.model.abstractModel import AbstractModel
import myokit

class Model(AbstractModel):
    def read_mmt_file(self):
        # calls self.mmtfile to read
        # sets variables: initial values, myokit model, protocol, parameters, units

        #Set up Myokit Model
        self._set_model()

        # List of Initial States
        self.initial_values = self.model.state()

        #Name of Central Compartment
        self.central_compartment_name = next(self.model.states()).qname()

        #Number of States
        self.dimension = len(self.initial_values)

        #Dictionary of Parameters
        self.parameter_component_name = 'param'
        self.params = {var.qname(): var.eval() for var in self.model.get(self.parameter_component_name).variables()}

    def set_mmt_file(self, filename):
        self.mmtfile = filename

    def set_initial_values(self, initial_values):
        """
        Sets initial values (state) in myokit model
        :param initial_values: list
        :return:
        """
        #Update in MyokitModel
        self.model.set_state(initial_values)

        #Update in Attributes
        self.initial_values = self.model.state()

    def _set_model(self):
        self.model, self.protocol, _ = myokit.load(self.mmtfile)

    def set_protocol(self, protocol):
        """
        :param protocol: myokit protocol object
        :return:
        """
        self.protocol = protocol

    def set_params(self, params):
        # Input as keyword args/dictionary? Output if incorrect?
        for name, value in params.items():
            if name in self.params: # check variable exists
                self.params[name] = value # update attributes
                self.model.set_value(name, value) # update model

    def get_mmt_file(self):
        return self.mmtfile

    def get_initial_values(self):
        return self.initial_values

    def _get_model(self):
        return self.model

    def get_protocol(self):
       return self.protocol

    def get_params(self):
        # Could add function to return specific parameter?
        return self.params

    def solve(self, duration, log_times=None, abs_tol=1e-11, rel_tol=1e-11):

        self.sim = myokit.Simulation(self.model, self.protocol)
        self.sim.set_tolerance(abs_tol=abs_tol, rel_tol=rel_tol)
        self.results = self.sim.run(duration, log_times=log_times)

    def get_solution(self, state_name):
        return self.results.get(state_name)



