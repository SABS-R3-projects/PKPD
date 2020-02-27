from pints import SingleOutputProblem

class AbstractInverseProblem(object):
    """Abstract class for inverse problems. Daughter classes will specifiy into SingleOutputInverseProblems and MultiOutputInverseProblems
    basing on pints.SingleOutputProblem and pints.MultiOutputProblem. For more information, see pints documentation https://pints.readthedocs.io/.
    """
    def find_optimal_parameter(self):
        """Find point in parameter space that optimises the objective function, i.e. find the set of parameters that minimises the
        distance of the model to the data with respect to the objective function.
        """
        raise NotImplementedError

    def set_error_function(self):
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