from typing import List

import numpy as np
import pints

from PKPD.inference.abstractInference import AbstractSingleOutputProblem

class SingleOutputProblem(AbstractSingleOutputProblem):
    """SingleOutputProblem according to pints https://pints.readthedocs.io/. Default objective function
    is pints.SumOfSquaresError and default optimiser is pints.CMAES.
    """
    def __init__(self, model: pints.ForwardModel, times: np.ndarray, values: np.ndarray):
        """Initialises a single output inference problem with default objective function pints.SumOfSquaresError
        and default optimiser pints.CMAES. Standard deviation in initial starting point of optimisation as well as
        restricted domain of support for inferred parameters is disabled by default.

        Arguments:
            model {pints.ForwardModel} -- Model which parameters are to be inferred.
            times {np.ndarray} -- Times of data points.
            values {np.ndarray} -- State values of data points.

        Return:
            None
        """
        super(SingleOutputProblem, self).__init__(model, times, values)

        self.objective_function = pints.SumOfSquaresError
        self.optimiser = pints.CMAES
        self.initial_parameter_uncertainty = None
        self.parameter_boundaries = None

    def find_optimal_parameter(self, initial_parameter: np.ndarray) -> None:
        """Find point in parameter space that optimises the objective function, i.e. find the set of parameters that minimises the
        distance of the model to the data with respect to the objective function.

        Arguments:
            initial_parameter {np.ndarray} -- Starting point in parameter space of the optimisation algorithm.

        Return:
            None
        """
        optimisation = pints.OptimisationController(function=self.objective_function,
                                              x0=initial_parameter,
                                              sigma0=self.initial_parameter_uncertainty,
                                              boundaries=self.parameter_boundaries,
                                              method=self.optimiser)

        self.estimated_parameters, self.objective_score = optimisation.run()

    def set_objective_function(self, objective_function: pints.ErrorMeasure) -> None:
        """Sets the objective function which is minimised to find the optimal parameter set.

        Arguments:
            objective_function {pints.ErrorMeasure} -- [description]
        
        Raises:
            ValueError: [description]
        """
        valid_obj_func = [pints.MeanSquaredError, pints.RootMeanSquaredError, pints.SumOfSquaresError]

        if objective_function not in valid_obj_func:
            raise ValueError('Objective function is not supported.')

        self.objective_function = objective_function

    def set_optimiser(self, optimiser: pints.Optimiser) -> None:
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.PSO, pints.SNES, pints.XNES]

        if optimiser not in valid_optimisers:
            raise ValueError('Method is not supported.')

        self.optimiser = optimiser

    def get_estimate(self) -> List:
        return [self.estimated_parameters, self.objective_score]



