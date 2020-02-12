from typing import List, Dict

import numpy as np
import pints

from PKPD.model import model as m
from PKPD.inference.abstractInference import AbstractInverseProblem


class SingleOutputInverseProblem(AbstractInverseProblem):
    """Single-output inverse problem based on pints.SingleOutputProblem https://pints.readthedocs.io/. Default objective function
    is pints.SumOfSquaresError and default optimiser is pints.CMAES.
    """
    def __init__(self, model: m.SingleOutputModel, times: np.ndarray, values: np.ndarray):
        """Initialises a single output inference problem with default objective function pints.SumOfSquaresError
        and default optimiser pints.CMAES. Standard deviation in initial starting point of optimisation as well as
        restricted domain of support for inferred parameters is disabled by default.

        Arguments:
            model {m.SingleOutputModel} -- Model which parameters are to be inferred.
            times {np.ndarray} -- Times of data points.
            values {np.ndarray} -- State values of data points.

        Return:
            None
        """
        self.problem = pints.SingleOutputProblem(model, times, values)
        self.objective_function = pints.SumOfSquaresError(self.problem)
        self.optimiser = pints.CMAES
        self.initial_parameter_uncertainty = None
        self.parameter_boundaries = None

        self.estimated_parameters = None
        self.objective_score = None


    def find_optimal_parameter(self, initial_parameter:np.ndarray) -> None:
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
            objective_function {pints.ErrorMeasure} -- Valid objective functions are [MeanSquaredError,
            RootMeanSquaredError, SumOfSquaresError] in pints.
        """
        valid_obj_func = [pints.MeanSquaredError, pints.RootMeanSquaredError, pints.SumOfSquaresError]

        if objective_function not in valid_obj_func:
            raise ValueError('Objective function is not supported.')

        self.objective_function = objective_function(self.problem)


    def set_optimiser(self, optimiser: pints.Optimiser) -> None:
        """Sets the optimiser to find the "global" minimum of the objective function.

        Arguments:
            optimiser {pints.Optimiser} -- Valid optimisers are [CMAES, NelderMead, PSO, SNES, XNES] in pints.
        """
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.SNES, pints.XNES]

        if optimiser not in valid_optimisers:
            raise ValueError('Method is not supported.')

        self.optimiser = optimiser


    def set_parameter_boundaries(self, boundaries:List):
        """Sets the parameter boundaries for inference.

        Arguments:
            boundaries {List} -- List of two lists. [min values, max values]
        """
        print('boundaries are ' + str(boundaries))
        if boundaries is None:
            self.parameter_boundaries = None
        else:
            min_values, max_values = boundaries[0], boundaries[1]
            self.parameter_boundaries = pints.RectangularBoundaries(min_values, max_values)


class MultiOutputInverseProblem(AbstractInverseProblem):
    """Multi-output inverse problem based on pints.MultiOutputProblem https://pints.readthedocs.io/. Default objective function
    is pints.SumOfSquaresError and default optimiser is pints.CMAES.
    """
    def __init__(self, model: m.MultiOutputModel, times: np.ndarray, values: np.ndarray):
        """Initialises a multi-output inference problem with default objective function pints.SumOfSquaresError
        and default optimiser pints.CMAES. Standard deviation in initial starting point of optimisation as well as
        restricted domain of support for inferred parameters is disabled by default.

        Arguments:
            model {m.MultiOutputModel} -- Model which parameters are to be inferred.
            times {np.ndarray} -- Times of data points.
            values {np.ndarray} -- State values of data points.

        Return:
            None
        """
        self.problem = pints.MultiOutputProblem(model, times, values)
        self.objective_function = pints.SumOfSquaresError(self.problem)
        self.optimiser = pints.CMAES
        self.initial_parameter_uncertainty = None
        self.parameter_boundaries = None

        self.estimated_parameters = None
        self.objective_score = None


    def find_optimal_parameter(self, initial_parameter:np.ndarray) -> None:
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
            objective_function {pints.ErrorMeasure} -- Valid objective functions are [MeanSquaredError,
            SumOfSquaresError] in pints.
        """
        valid_obj_func = [pints.MeanSquaredError, pints.SumOfSquaresError]

        if objective_function not in valid_obj_func:
            raise ValueError('Objective function is not supported.')

        self.objective_function = objective_function(self.problem)


    def set_optimiser(self, optimiser: pints.Optimiser) -> None:
        """Sets the optimiser to find the "global" minimum of the objective function.

        Arguments:
            optimiser {pints.Optimiser} -- Valid optimisers are [CMAES, NelderMead, PSO, SNES, XNES] in pints.
        """
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.SNES, pints.XNES]

        if optimiser not in valid_optimisers:
            raise ValueError('Method is not supported.')

        self.optimiser = optimiser


    def set_parameter_boundaries(self, boundaries:List):
        """Sets the parameter boundaries for inference.

        Arguments:
            boundaries {List} -- List of two lists. [min values, max values]
        """
        min_values, max_values = boundaries[0], boundaries[1]
        self.parameter_boundaries = pints.RectangularBoundaries(min_values, max_values)