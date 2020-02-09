import unittest

import pints
import pytest
import numpy as np

from PKPD.model import model as m
from PKPD.inference import inference


class TestSingleOutputProblem(unittest.TestCase):
    """Testing the methods of the SingleOutputinverseProblem class.
    """
    ## Test case: Linear One Compartment Model with Bolus dosing
    # generating data
    file_name = 'PKPD/modelRepository/1comp_bolus_linear.mmt'
    one_comp_model = m.SingleOutputModel(file_name)
    true_parameters_one_comp_model = [2, 2, 4] # # [initial drug, CL, V]

    times = np.linspace(0.0, 24.0, 100)
    model_result = one_comp_model.simulate(true_parameters_one_comp_model, times)

    # add white noise to generate data
    scale = np.mean(model_result) * 0.05 # arbitrary choice of noise (not too much, not too little)
    data_one_comp_model = model_result + np.random.normal(loc=0.0,
                                                         scale=scale,
                                                         size=len(model_result)
                                                         )


    def test_find_optimal_parameter(self):
        """Test whether the find_optimal_parameter method works as expected.
        """
        problem = inference.SingleOutputInverseProblem(model=self.one_comp_model,
                                                       times=self.times,
                                                       values=self.data_one_comp_model
                                                       )

        # start somewhere in parameter space (close to the solution for ease)
        initial_parameters = np.array([1, 3, 5])

        # solve inverse problem
        problem.find_optimal_parameter(initial_parameter=initial_parameters)
        estimated_paramters = problem.estimated_parameters

        for parameter_id, true_value in enumerate(self.true_parameters_one_comp_model):
            estimated_value = estimated_paramters[parameter_id]
            assert true_value == pytest.approx(estimated_value, rel=0.05)


    def test_set_objective_function(self):
        """Test whether the set_objective_function method works as expected.
        """
        problem = inference.SingleOutputInverseProblem(model=self.one_comp_model,
                                                       times=self.times,
                                                       values=self.data_one_comp_model
                                                       )

        # iterate through valid error measures
        valid_obj_func = [pints.MeanSquaredError, pints.RootMeanSquaredError, pints.SumOfSquaresError]
        for obj_func in valid_obj_func:
            problem.set_objective_function(objective_function=obj_func)

            # assert that error measure is set as expected
            assert type(obj_func(problem.problem)) == type(problem.objective_function)


    def test_set_optimiser(self):
        """Test whether the set_optimiser method works as expected. The estimated values
        are not of interest but rather whether the optimiser are properly embedded.
        """
        problem = inference.SingleOutputInverseProblem(model=self.one_comp_model,
                                                       times=self.times,
                                                       values=self.data_one_comp_model
                                                       )

        # solve inverse problem
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.PSO, pints.SNES, pints.XNES]
        for opt in valid_optimisers:
            problem.set_optimiser(optimiser=opt)

            assert opt == problem.optimiser


class TestMultiOutputProblem(unittest.TestCase):
    """Testing the methods of MultiOutputInverseProblem class.
    """
    ## Test case I: One Compartment Model
    # generating data
    file_name = 'PKPD/mmt/one_compartment.mmt'
    one_comp_model = m.MultiOutputModel(file_name)
    true_parameters_one_comp_model = [20, 2, 4] # [bolus.y_c, param.CL, param.V_c]

    times = np.linspace(0.0, 24.0, 10000)
    model_result = one_comp_model.simulate(true_parameters_one_comp_model, times)

    # add white noise to generate data
    scale = np.mean(model_result) * 0.05 # arbitrary choice of noise (not too much, not too little)
    noise =  np.random.normal(loc=0.0,
                              scale=scale,
                              size=model_result.shape
                              )
    data_one_comp_model = model_result + noise


    def test_find_optimal_parameter(self):
        """Test whether the find_optimal_parameter method works as expected.
        """
        problem = inference.MultiOutputInverseProblem(model=self.one_comp_model,
                                                      times=self.times,
                                                      values=self.data_one_comp_model
                                                      )

        # start somewhere in parameter space (close to the solution for ease)
        initial_parameters = np.array([25, 3, 5])

        # solve inverse problem
        problem.find_optimal_parameter(initial_parameter=initial_parameters)
        parameter_dict, _ = problem.get_estimate()

        for parameter_id, parameter_name in enumerate(parameter_dict):
            true_value = self.true_parameters_one_comp_model[parameter_id]
            estimated_value = parameter_dict[parameter_name]
            assert true_value == pytest.approx(estimated_value, rel=0.05)


    def test_set_objective_function(self):
        """Test whether the set_objective_function method works as expected.
        """
        problem = inference.MultiOutputInverseProblem(model=self.one_comp_model,
                                                       times=self.times,
                                                       values=self.data_one_comp_model
                                                       )

        # start somewhere in parameter space (close to the solution for ease)
        initial_parameters = np.array([20.1, 2.1, 4.1])

        # solve inverse problem
        valid_obj_func = [pints.MeanSquaredError, pints.SumOfSquaresError]
        for obj_func in valid_obj_func:
            problem.set_objective_function(objective_function=obj_func)
            problem.find_optimal_parameter(initial_parameter=initial_parameters)
            parameter_dict, _ = problem.get_estimate()

            for parameter_id, parameter_name in enumerate(parameter_dict):
                true_value = self.true_parameters_one_comp_model[parameter_id]
                estimated_value = parameter_dict[parameter_name]
                assert true_value == pytest.approx(estimated_value, rel=0.05)


    def test_optimiser(self):
        """Test whether the set_optimiser method works as expected. The estimated values
        are not of interest but rather whether the optimiser are properly embedded.
        """
        problem = inference.MultiOutputInverseProblem(model=self.one_comp_model,
                                                        times=self.times,
                                                        values=self.data_one_comp_model
                                                        )

        # start somewhere in parameter space (close to the solution for ease)
        initial_parameters = np.array([20.1, 2.1, 4.1])

        # solve inverse problem
        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.SNES, pints.XNES]
        for opt in valid_optimisers:
            problem.set_optimiser(optimiser=opt)
            problem.find_optimal_parameter(initial_parameter=initial_parameters)
            parameter_dict, _ = problem.get_estimate()

            for parameter_id, parameter_name in enumerate(parameter_dict):
                true_value = self.true_parameters_one_comp_model[parameter_id]
                estimated_value = parameter_dict[parameter_name]
                assert true_value == pytest.approx(estimated_value, rel=0.05)
