from typing import List

import numpy as np
import pints

from PKPD.model.model import Model
from PKPD.inference.abstractInference import AbstractSingleOutputInverseProblem


class Myokit2PintsModelWrapper(pints.ForwardModel):
    """Wrapper of the myokit forward model to a pints forward model
    for compatibility with pints inference tools.
    """
    def __init__(self, model:Model):
        """Initiates the wrapped model.

        Arguments:
            model {Model} -- Myokit model.
        """
        super(Myokit2PintsModelWrapper, self).__init__()
        self.myokit_model = model
        self.model_param_keys = self._get_keys()
        self.n_initial_conditions = len(self.myokit_model.get_initial_values())

    def _get_keys(self):
        """Returns model parameter names in alphabetical order.

        Returns:
            {List} -- List of strings with the keys of the model parameters.
        """
        return sorted(self.myokit_model.get_params())

    def n_parameters(self):
        """Returns number of parameters to be fitted in the model, i.e. the mnodel
        parameters and the initial conditions.

        Returns:
            {int} -- number of parameters for optimisation.
        """
        n_model_params = len(self.model_param_keys)
        n_params = n_model_params + self.n_initial_conditions
        return n_params

    def simulate(self, parameters:np.ndarray, times:np.ndarray):
        """Solves the forward problem using the myokit model.

        Arguments:
            parameters {np.ndarray} -- parameters of the model for optimisation.
            times {np.ndarray} -- times at which the simulation is evaluated.
        
        Returns:
            {np.ndarray} -- state values corresponding to the input times.
        """
        initial_conditions, model_parameters = self._split_parameters(parameters)
        self.myokit_model.set_params(model_parameters)
        self.myokit_model.set_initial_values(initial_conditions)

        # duration of simulation (plus 1 to keep the final time step)
        duration = times[-1] - times[0] + 1
        # name of compartment
        main_compartment = self.myokit_model.central_compartment_name

        self.myokit_model.solve(duration=duration, log_times=times)
        values = self.myokit_model.get_solution(main_compartment)

        return np.array(values)

    def _split_parameters(self, parameters:np.ndarray):
        """Separates the parameters for optimisation back into intitial
        values of the state and model parameters.

        Arguments:
            parameters {nd.array} -- Parameters that are optimised.

        Return:
            {List} -- [initial conditions, model parameters]
        """
        initial_conditions = parameters[:self.n_initial_conditions]
        model_parameters = dict(zip(self.model_param_keys,
                                    parameters[self.n_initial_conditions:]
                                    )
                                )
        return [initial_conditions, model_parameters]


class SingleOutputInverseProblem(AbstractSingleOutputInverseProblem):
    """Single output inverse problem based on pints.SingleOutputProblem https://pints.readthedocs.io/. Default objective function
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
        self.problem = pints.SingleOutputProblem(model, times, values)
        self.objective_function = pints.SumOfSquaresError(self.problem)
        self.optimiser = pints.CMAES
        self.initial_parameter_uncertainty = None
        self.parameter_boundaries = None
        self.iterations = 200 # default value from pints
        self.threshold = 1e-11 # default value from pints

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
        optimisation.set_max_unchanged_iterations(iterations=self.iterations,
                                                  threshold=self.threshold)

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
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.PSO, pints.SNES, pints.XNES]

        if optimiser not in valid_optimisers:
            raise ValueError('Method is not supported.')

        self.optimiser = optimiser

    def get_estimate(self) -> List:
        """Returns the estimated parameters that minimise the objective function.

        Returns:
            List -- [initial condition, model parameters, corresponding score of the objective function]
        """
        if self.estimated_parameters is None:
            raise ValueError('The estimated parameter is None. Try to run the `find_optimal_parameter` routine again?')
        initial_conditions, model_parameters = self.problem._model._split_parameters(self.estimated_parameters)

        return [initial_conditions, model_parameters, self.objective_score]

    def set_max_unchanged_iterations(self, iterations=200, threshold=1e-11):
        """Setting the convergence criterion of the optimisation controller

        Arguments:
            iterations {int} -- Number of iterations in objective function does not change. (default: {200})
            threshold {[type]} -- Precision for objective scores. (default: {1e-11})
        """
        self.iterations = iterations
        self.threshold = threshold



