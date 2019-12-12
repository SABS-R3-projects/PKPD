from pints import SingleOutputProblem

# class AbstractInference(ABC):
#     def __init__(self):
#         pass

#     @abstractmethod
#     def infer_parameters(self):
#         # infer the parameters
#         raise NotImplementedError

#     @abstractmethod
#     def set_objective_func(self):
#         # set the function that should be minimised, takes string input eg least squares
#         raise NotImplementedError

#     @abstractmethod
#     def find_optima(self):
#         # find the optimum for stuff
#         raise NotImplementedError

#     @abstractmethod
#     def find_posterior(self):
#         # find the posterior
#         raise NotImplementedError

#     @abstractmethod
#     def set_optimiser(self):
#         # set the method used for optimisation (used in find_optima)
#         raise NotImplementedError

#     @abstractmethod
#     def set_sampling_method(self):
#         # set algorithm, eg MCMC, in pints
#         raise NotImplementedError

#     @abstractmethod
#     def set_initial_values(self):
#         # set the initial values
#         raise NotImplementedError

#     @abstractmethod
#     def set_prior(self):
#         # set the prior
#         raise NotImplementedError

#     @abstractmethod
#     def set_bounds(self):
#         # set the boundaries (if separately to prior)
#         raise NotImplementedError

#     @abstractmethod
#     def load_data(self):
#         # take data from data class
#         raise NotImplementedError

#     @abstractmethod
#     def fix_parameters(self):
#         # tell it which parameters to fix the values of
#         raise NotImplementedError

#     @abstractmethod
#     def log_inferred_parameters(self):
#         # save the parameters that have been inferred
#         raise NotImplementedError

class AbstractSingleOutputProblem(SingleOutputProblem):
    """Abstract wrapper around pints.SingleOutputProblem. A SingleOutputProblem represents an inference problem where a model is fit
    to a single time series, such as measured from a system with a single output. For more information see pints documentation
    https://pints.readthedocs.io/.
    """
    def __init__(self, model, times, values):
        super(AbstractSingleOutputProblem, self).__init__(model, times, values)

    def find_optimal_parameter(self):
        """Find point in parameter space that optimises the objective function, i.e. find the set of parameters that minimises the
        distance of the model to the data with respect to the objective function.
        """
        raise NotImplementedError

    def set_objective_function(self):
        """Sets objective function which is minimised to find parameters. Allowed objective functions are those implemented in
        pints, i.e. MeanSquaredError, RootMeanSquaredError, SumOfSquaresError. ProbabilityBasedError and SumOfErrors are not yet
        supported. For more information see pints documentation https://pints.readthedocs.io/.
        """
        raise NotImplementedError

    def set_optimiser(self):
        """Sets method to minimise objective function. Allowed methods are those implemented in pints, i.e. CMA-ES, Nelder-Mead,
        PSO, SNES, xNES. For more information see pints documentation https://pints.readthedocs.io/.
        """
        raise NotImplementedError