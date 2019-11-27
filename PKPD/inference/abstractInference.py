from abc import ABC, abstractmethod

class AbstractInference(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def infer_parameters(self):
        # infer the parameters
        raise NotImplementedError

    @abstractmethod
    def set_objective_func(self):
        # set the function that should be minimised, takes string input eg least squares
        raise NotImplementedError

    @abstractmethod
    def find_optima(self):
        # find the optimum for stuff
        raise NotImplementedError

    @abstractmethod
    def find_posterior(self):
        # find the posterior
        raise NotImplementedError

    @abstractmethod
    def set_optimiser(self):
        # set the method used for optimisation (used in find_optima)
        raise NotImplementedError

    @abstractmethod
    def set_sampling_method(self):
        # set algorithm, eg MCMC, in pints
        raise NotImplementedError

    @abstractmethod
    def set_initial_values(self):
        # set the initial values
        raise NotImplementedError

    @abstractmethod
    def set_prior(self):
        # set the prior
        raise NotImplementedError

    @abstractmethod
    def set_bounds(self):
        # set the boundaries (if separately to prior)
        raise NotImplementedError

    @abstractmethod
    def load_data(self):
        # take data from data class
        raise NotImplementedError

    @abstractmethod
    def fix_parameters(self):
        # tell it which parameters to fix the values of
        raise NotImplementedError

    @abstractmethod
    def log_inferred_parameters(self):
        # save the parameters that have been inferred
        raise NotImplementedError
