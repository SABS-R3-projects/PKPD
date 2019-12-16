from pints import SingleOutputProblem

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

    def get_estimate(self):
        """Returns the estimated parameters as well as their objective function score.
        """
        raise NotImplementedError