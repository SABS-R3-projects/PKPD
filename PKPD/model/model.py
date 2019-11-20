from abstractModel import AbstractModel
import myokit

class Model(AbstractModel):
    def read_mmt_file(self):
        # calls self.mmtfile to read
        # sets variables: initial values, myokit model, protocol, parameters, units

        #Set up Myokit Model
        self._set_model()

        # List of Initial States
        self.initial_values = self.model.state()

        #Number of States
        self.dimension = len(self.initial_values)

        #Dictionary of Parameters
        self.params = {var.qname(): var.eval() for var in self.model.variables()}

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
        # set parameter values
        raise NotImplementedError

    def get_mmt_file(self):
        return self.mmtfile

    def get_initial_values(self):
        return self.initial_values

    def _get_model(self):
        return self.model

    def get_protocol(self):
       return self.protocol

    def get_params(self):
        return self.params

    def solve(self):
        # use myokit to solve problem
        raise NotImplementedError

    def get_solution(self):
        # gets the solution
        raise NotImplementedError



    # Extra Functions


