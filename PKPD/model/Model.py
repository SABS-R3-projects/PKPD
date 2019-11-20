from abstractModel import AbstractModel
import myokit

class Model(AbstractModel):
    def set_mmt_file(self, filename):
        self.mmtfile = filename

    def read_mmt_file(self):
        # calls self.mmtfile to read
        # sets variables: initial values, myokit model, protocol, parameters, units
        raise NotImplementedError

