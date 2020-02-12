from typing import List, Dict

import numpy as np
import pints

from PKPD.model import model as m
from PKPD.inference.abstractInference import AbstractInverseProblem


class SingleOutputInverseProblem(AbstractInverseProblem):
    """Single-output inverse problem based on pints.SingleOutputProblem https://pints.readthedocs.io/. Default objective function
    is pints.SumOfSquaresError and default optimiser is pints.CMAES.
    """

    def __init__(self, models: dict, data: dict):
        """Initialises a single output inference problem with default objective function pints.SumOfSquaresError
        and default optimiser pints.CMAES. Standard deviation in initial starting point of optimisation as well as
        restricted domain of support for inferred parameters is disabled by default.

        Arguments:
            models {dict} -- A dictionary of Models (m.SingleOutputModel) for each patient ID on which parameters are to
                be inferred.
            data {dict} -- A dictionary of tuples for each patient ID, where the the tuple contains an np.ndarray of
                times and an np.ndarray of state values.

        Return:
            None
        """
        self.problems = []
        self.error_measure = None
        self.patients_data = data

        for i in models:
            self.problems.append(
                pints.SingleOutputProblem(models[i], self.patients_data[i][0], self.patients_data[i][1]))

        self.objective_function = None
        self.set_objective_function(pints.SumOfSquaresError)

        self.optimiser = pints.CMAES
        self.initial_parameter_uncertainty = None
        self.parameter_boundaries = None

        self.estimated_parameters = None
        self.objective_score = None


    def find_optimal_parameter(self, initial_parameter:np.ndarray, number_of_iterations:int=5) -> None:
        """Find point in parameter space that optimises the objective function, i.e. find the set of parameters that minimises the
        distance of the model to the data with respect to the objective function. Optimisation is run number_of_iterations times and
        result with minimal score is returned.

        Arguments:
            initial_parameter {np.ndarray} -- Starting point in parameter space of the optimisation algorithm.
            number_of_iterations {int} -- Number of times optimisation is run. Default: 5 (arbitrary).

        Return:
            None
        """
        # set default randomness in initial parameter values, if not specified in GUI
        if self.initial_parameter_uncertainty is None:
            # TODO: evaluate how to choose uncertainty best, to obtain most stable results
            self.initial_parameter_uncertainty = initial_parameter + 0.1 # arbitrary

        # initialise optimisation
        optimisation = pints.OptimisationController(function=self.objective_function,
                                                    x0=initial_parameter,
                                                    sigma0=self.initial_parameter_uncertainty,
                                                    boundaries=self.parameter_boundaries,
                                                    method=self.optimiser)

        # run optimisation 'number_of_iterations' times
        estimate_container = []
        score_container = []
        for _ in range(number_of_iterations):
            estimates, score = optimisation.run()
            estimate_container.append(estimates)
            score_container.append(score)

        # return parameters with minimal score
        min_score_id = np.argmin(score_container)
        self.estimated_parameters, self.objective_score = [estimate_container[min_score_id], score_container[min_score_id]]

    def set_objective_function(self, error_measure: pints.ErrorMeasure) -> None:
        """Sets the objective function which is minimised to find the optimal parameter set.

        Arguments:
            objective_function {pints.ErrorMeasure} -- Valid objective functions are [MeanSquaredError,
            RootMeanSquaredError, SumOfSquaresError] in pints.
        """
        valid_obj_func = [pints.MeanSquaredError, pints.RootMeanSquaredError, pints.SumOfSquaresError]

        if error_measure not in valid_obj_func:
            raise ValueError('Objective function is not supported.')

        self.errors = []

        for problem in self.problems:
            problem_i = problem
            self.errors.append(error_measure(problem_i))

        self.objective_function = pints.SumOfErrors(self.errors)

    def set_optimiser(self, optimiser: pints.Optimiser) -> None:
        """Sets the optimiser to find the "global" minimum of the objective function.

        Arguments:
            optimiser {pints.Optimiser} -- Valid optimisers are [CMAES, NelderMead, PSO, SNES, XNES] in pints.
        """
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.PSO, pints.SNES, pints.XNES]

        if optimiser not in valid_optimisers:
            raise ValueError('Method is not supported.')

        self.optimiser = optimiser

    def set_parameter_boundaries(self, boundaries: List):
        """Sets the parameter boundaries for inference.

        Arguments:
            boundaries {List} -- List of two lists. [min values, max values]
        """
        min_values, max_values = boundaries[0], boundaries[1]
        self.parameter_boundaries = pints.RectangularBoundaries(min_values, max_values)


class MultiOutputInverseProblem(AbstractInverseProblem):
    """Multi-output inverse problem based on pints.MultiOutputProblem https://pints.readthedocs.io/. Default objective function
    is pints.SumOfSquaresError and default optimiser is pints.CMAES.
    """

    def __init__(self, models: dict, data: dict):
        """Initialises a multi-output inference problem with default objective function pints.SumOfSquaresError
        and default optimiser pints.CMAES. Standard deviation in initial starting point of optimisation as well as
        restricted domain of support for inferred parameters is disabled by default.

        Arguments:
            models {dict} -- A dictionary of Models (m.MultiOutputModel) for each patient ID on which parameters are to
                be inferred.
            data {dict} -- A dictionary of tuples for each patient ID, where the the tuple contains an np.ndarray of
                times and an np.ndarray of state values.
        Return:
            None
        """

        self.problems = []
        self.error_measure = None
        self.patients_data = data

        for i in models:
            x = np.asarray(self.patients_data[i][0][:])
            y = np.asarray(self.patients_data[i][1][:])
            self.problems.append(pints.MultiOutputProblem(models[i], x, y))

        self.objective_function = None
        self.set_objective_function(pints.SumOfSquaresError)

        self.optimiser = pints.CMAES
        self.initial_parameter_uncertainty = None
        self.parameter_boundaries = None

        self.estimated_parameters = None
        self.objective_score = None


    def find_optimal_parameter(self, initial_parameter:np.ndarray, number_of_iterations:int=5) -> None:
        """Find point in parameter space that optimises the objective function, i.e. find the set of parameters that minimises the
        distance of the model to the data with respect to the objective function.

        Arguments:
            initial_parameter {np.ndarray} -- Starting point in parameter space of the optimisation algorithm.

        Return:
            None
        """
        # set default randomness in initial parameter values, if not specified in GUI
        if self.initial_parameter_uncertainty is None:
            # TODO: evaluate how to choose uncertainty best, to obtain most stable results
            self.initial_parameter_uncertainty = initial_parameter + 0.1 # arbitrary

        # initialise optimisation
        optimisation = pints.OptimisationController(function=self.objective_function,
                                                    x0=initial_parameter,
                                                    sigma0=self.initial_parameter_uncertainty,
                                                    boundaries=self.parameter_boundaries,
                                                    method=self.optimiser)

        # run optimisation 'number_of_iterations' times
        estimate_container = []
        score_container = []
        for _ in range(number_of_iterations):
            estimates, score = optimisation.run()
            estimate_container.append(estimates)
            score_container.append(score)
            print(estimates)
            print(score)

        # return parameters with minimal score
        min_score_id = np.argmin(score_container)
        self.estimated_parameters, self.objective_score = [estimate_container[min_score_id], score_container[min_score_id]]

    def set_objective_function(self, error_measure: pints.ErrorMeasure) -> None:
        """Sets the objective function which is minimised to find the optimal parameter set.

        Arguments:
            error_measure {pints.ErrorMeasure} -- Valid objective functions are [MeanSquaredError,
            SumOfSquaresError] in pints.
        """
        valid_obj_func = [pints.MeanSquaredError, pints.SumOfSquaresError]

        if error_measure not in valid_obj_func:
            raise ValueError('Objective function is not supported.')

        self.errors = []

        for problem in self.problems:
            problem_i = problem
            self.errors.append(error_measure(problem_i))

        self.objective_function = pints.SumOfErrors(self.errors)

    def set_optimiser(self, optimiser: pints.Optimiser) -> None:
        """Sets the optimiser to find the "global" minimum of the objective function.

        Arguments:
            optimiser {pints.Optimiser} -- Valid optimisers are [CMAES, NelderMead, PSO, SNES, XNES] in pints.
        """
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.PSO, pints.SNES, pints.XNES]

        if optimiser not in valid_optimisers:
            raise ValueError('Method is not supported.')

        self.optimiser = optimiser

    def set_parameter_boundaries(self, boundaries: List):
        """Sets the parameter boundaries for inference.

        Arguments:
            boundaries {List} -- List of two lists. [min values, max values]
        """
        min_values, max_values = boundaries[0], boundaries[1]
        self.parameter_boundaries = pints.RectangularBoundaries(min_values, max_values)