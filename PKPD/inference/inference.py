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
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.SNES, pints.XNES]

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

    def get_estimate(self) -> List:
        """Returns the estimated parameters that minimise the objective function in a dictionary and the corresponding
        score of the objective function.

        Returns:
            List -- [parameter dictionary, corresponding score of the objective function]
        """
        if self.estimated_parameters is None:
            raise ValueError('The estimated parameter is None. Try to run the `find_optimal_parameter` routine again?')
        parameter_dict = self._create_parameter_dict(self.estimated_parameters)

        return [parameter_dict, self.objective_score]

    def _create_parameter_dict(self, estimated_parameter: np.ndarray) -> Dict:
        """Creates a dictionary of the optimal parameters by assigning the corresponding names to them.

        Arguments:
            estimated_parameter {np.ndarray} -- Parameter values resulting from the optimisation.

        Return:
            {Dict} -- Estimated parameter values with their name as key.
        """
        state_dimension = 1
        state_name = self.problems[0]._model.state_name
        parameter_names = self.problems[0]._model.parameter_names

        parameter_dict = {}
        # Note that the estimated parameters are [initial values, model parameter].
        for parameter_id, value in enumerate(estimated_parameter):
            if parameter_id < state_dimension:
                parameter_dict[state_name] = value
            else:
                reset_id = parameter_id - state_dimension
                parameter_dict[parameter_names[reset_id]] = value

        return parameter_dict


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
        print('inf 1')
        print(models)

        for i in models:
            x = np.asarray(self.patients_data[i][0][:])
            print('infmodel', x.shape)
            y = np.asarray(self.patients_data[i][1][:])
            print('infmodel', y.shape)
            print(models[i].n_outputs())
            self.problems.append(pints.MultiOutputProblem(models[i], x, y))
            print('infmodel', i)

        self.objective_function = None
        self.set_objective_function(pints.SumOfSquaresError)
        print('inf', 2)

        self.optimiser = pints.CMAES
        self.initial_parameter_uncertainty = None
        self.parameter_boundaries = None
        print('inf', 3)

        self.estimated_parameters = None
        self.objective_score = None
        print('inf', 4)

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
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.SNES, pints.XNES]

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

    def get_estimate(self) -> List:
        """Returns the estimated parameters that minimise the objective function in a dictionary and the corresponding
        score of the objective function.

        Returns:
            List -- [parameter dictionary, corresponding score of the objective function]
        """
        if self.estimated_parameters is None:
            raise ValueError('The estimated parameter is None. Try to run the `find_optimal_parameter` routine again?')
        parameter_dict = self._create_parameter_dict(self.estimated_parameters)

        return [parameter_dict, self.objective_score]

    def _create_parameter_dict(self, estimated_parameter: np.ndarray) -> Dict:
        """Creates a dictionary of the optimal parameters by assigning the corresponding names to them.

        Arguments:
            estimated_parameter {np.ndarray} -- Parameter values resulting from the optimisation.

        Return:
            {Dict} -- Estimated parameter values with their name as key.
        """
        state_dimension =  self.problems[0]._model.n_outputs()
        state_names =  self.problems[0]._model.state_names
        parameter_names =  self.problems[0]._model.parameter_names

        parameter_dict = {}
        # Note that the estimated parameters are [inital values, model parameter].
        for parameter_id, value in enumerate(estimated_parameter):
            if parameter_id < state_dimension:
                parameter_dict[state_names[parameter_id]] = value
            else:
                reset_id = parameter_id - state_dimension
                parameter_dict[parameter_names[reset_id]] = value

        return parameter_dict
