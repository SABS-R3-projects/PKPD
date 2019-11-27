from abc import ABC, abstractmethod

class AbstractModel(ABC):
    def __init__(self):
        self.mmtfile = None

    @abstractmethod
    def read_mmt_file(self):
        # calls self.mmtfile to read
        # sets variables: initial values, myokit model, protocol, parameters, units
        raise NotImplementedError

    @abstractmethod
    def set_mmt_file(self, filename):
        # set mmt file
        raise NotImplementedError

    @abstractmethod
    def set_initial_values(self):
        # set initial values
        raise NotImplementedError

    @abstractmethod
    def _set_model(self):
        # set myokit model
        raise NotImplementedError

    @abstractmethod
    def set_protocol(self):
        # set myokit protocol
        raise NotImplementedError

    @abstractmethod
    def set_params(self):
        # set parameter values
        raise NotImplementedError

    @abstractmethod
    def get_mmt_file(self, filename):
        # get mmt file
        raise NotImplementedError

    @abstractmethod
    def get_initial_values(self):
        # get initial values
        raise NotImplementedError

    @abstractmethod
    def _get_model(self):
        # get myokit model
        raise NotImplementedError

    @abstractmethod
    def get_protocol(self):
        # get myokit protocol
        raise NotImplementedError

    @abstractmethod
    def get_params(self):
        # get parameter values
        raise NotImplementedError

    @abstractmethod
    def solve(self):
        # use myokit to solve problem
        raise NotImplementedError

    @abstractmethod
    def get_solution(self):
        # gets the solution
        raise NotImplementedError
