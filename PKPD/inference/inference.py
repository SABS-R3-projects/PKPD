import numpy as np
from typing import List
from pints import OptimisationController
from pints import ErrorMeasure, MeanSquaredError, RootMeanSquaredError, SumOfSquaresError
from pints import Optimiser, CMAES, NelderMead, PSO, SNES, XNES

from PKPD.inference.abstractInference import AbstractSingleOutputProblem

class SingleOutputProblem(AbstractSingleOutputProblem):
    """SingleOutputProblem according to pints https://pints.readthedocs.io/. Default objective function
    is pints.SumOfSquaresError and default optimiser is pints.CMAES.
    """
    def __init__(self, model, times, values):
        super(SingleOutputProblem, self).__init__(model, times, values)

        self.objective_function = SumOfSquaresError
        self.optimiser = CMAES

    def find_optimal_parameter(self, initial_parameter: np.ndarray) -> None:
        if self.optimiser not in [CMAES, NelderMead, PSO, SNES, XNES]:
            raise NotImplementedError('Method is not supported.')
        if self.objective_function not in [MeanSquaredError, RootMeanSquaredError, SumOfSquaresError]:
            raise NotImplementedError('Objective function is not supported.')

        optimisation = OptimisationController(function=self.objective_function,
                                              x0=initial_parameter,
                                              sigma0=None,
                                              boundaries=None,
                                              method=self.optimiser)

        self.estimated_parameters, self.objective_score = optimisation.run()

    def set_objective_function(self, objective_function: ErrorMeasure) -> None:
        if objective_function not in [MeanSquaredError, RootMeanSquaredError, SumOfSquaresError]:
            raise NotImplementedError('Objective function is not supported.')

        self.objective_function = objective_function

    def set_optimiser(self, optimiser: Optimiser) -> None:
        if optimiser not in [CMAES, NelderMead, PSO, SNES, XNES]:
            raise NotImplementedError('Method is not supported.')

        self.optimiser = optimiser

    def get_estimate(self) -> List:
        return [self.estimated_parameters, self.objective_score]



