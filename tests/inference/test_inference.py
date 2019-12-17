import pytest
import unittest
import pints
import numpy as np

from PKPD.model import model
from PKPD.inference import inference


class TestMyokit2PintsModelWrapper(unittest.TestCase):
    """Tests whether the Myokit Model was properly wrapped into the pints
    interface.
    """
    def test_n_parameters(self):
        """Testing whether the wrapper returns the correct number of parameters
        to fit, i.e. model parameter and initial conditions.
        """
        # Test case I: One Compartment Model
        file_name = 'PKPD/mmt/one_compartment.mmt'

        myokit_model = model.Model()
        myokit_model.mmtfile = file_name
        myokit_model.read_mmt_file()

        true_number_params = (len(myokit_model.get_params())
                             + len(myokit_model.get_initial_values())
                             )

        wrapped_model = inference.Myokit2PintsModelWrapper(myokit_model)
        number_params = wrapped_model.n_parameters()

        assert number_params == true_number_params


    def test_simulate(self):
        """Testing whether the simulation of the wrapped model coincides
        with the simulation of the myokit model.
        """
        # Test case I: One Compartment Model
        file_name = 'PKPD/mmt/one_compartment.mmt'

        myokit_model = model.Model()
        myokit_model.mmtfile = file_name
        myokit_model.read_mmt_file()

        times = np.linspace(0.0, 24.0, 1000)
        duration = times[-1] - times[0] + 1 # plus 1 to keep final time step

        # Solve myokit model
        myokit_model.solve(duration=duration, log_times=times)
        np_myokit_times = np.array(myokit_model.get_solution('engine.time'))
        np_myokit_state_values = np.array(myokit_model.get_solution(myokit_model.central_compartment_name))

        # Wrapped model
        wrapped_model = inference.Myokit2PintsModelWrapper(myokit_model)

        ## get model parameters to run the simulation in the wrapped model
        # initial conditions by construction come first
        parameters = myokit_model.get_initial_values()
        # append model parameters
        params_keys = wrapped_model.model_param_keys
        param_dict = myokit_model.get_params()
        for param in params_keys:
            value = param_dict[param]
            parameters.append(value)

        # solve wrapped model
        state_values = wrapped_model.simulate(parameters, times)

        # assert times are matching
        assert np.allclose(times, np_myokit_times, atol=1e-07)
        # assert solutions are matching
        assert np.allclose(state_values, np_myokit_state_values, atol=1e-07)



class TestSingleOutputProblem(unittest.TestCase):
    """Testing the methods of SingleOutputProblem.
    """
    ## Test case: One Compartment Model
    # generating data
    file_name = 'PKPD/mmt/one_compartment.mmt'

    myokit_model = model.Model()
    myokit_model.mmtfile = file_name
    myokit_model.read_mmt_file()

    times = np.linspace(0.0, 24.0, 1000)
    duration = times[-1] - times[0] + 1 # plus 1 to keep final time step

    # Solve myokit model
    myokit_model.solve(duration=duration, log_times=times)
    np_myokit_state_values = np.array(myokit_model.get_solution(myokit_model.central_compartment_name))

    # add white noise to generate data
    scale = np.mean(np_myokit_state_values) * 0.05 # arbitrary choice of noise (not too much, not too little)
    data = np_myokit_state_values + np.random.normal(loc=0.0,
                                                     scale=scale,
                                                     size=len(np_myokit_state_values)
                                                     )

    # true initial values and parameters
    true_intitial_values = myokit_model.get_initial_values()
    true_model_parameters = myokit_model.get_params()


    def test_find_optimal_parameter(self):
        """Test whether the find_optimal_parameter method works as expected.
        """
        wrapped_model = inference.Myokit2PintsModelWrapper(self.myokit_model)
        problem = inference.SingleOutputInverseProblem(model=wrapped_model,
                                                       times=self.times,
                                                       values=self.data
                                                       )

        # start somewhere in parameter space (close to the solution for ease)
        initial_parameters = np.array([25.1, 3.1, 5.1])

        # solve inverse problem
        problem.set_max_unchanged_iterations(iterations=10, threshold=1e-5)
        problem.find_optimal_parameter(initial_parameter=initial_parameters)
        initial_values, model_parameters, _ = problem.get_estimate()

        assert self.true_intitial_values == pytest.approx(initial_values, rel=0.05)

        for key, true_value in self.true_model_parameters.items():
            value = model_parameters[key]
            assert true_value == pytest.approx(value, rel=0.05)

    def test_set_objective_function(self):
        """Test whether the set_objective_function method works as expected. The estimated values
        are not of interest but rather whether the objective functions are properly embedded.
        """
        wrapped_model = inference.Myokit2PintsModelWrapper(self.myokit_model)
        problem = inference.SingleOutputInverseProblem(model=wrapped_model,
                                                       times=self.times,
                                                       values=self.data
                                                       )

        # start somewhere in parameter space (close to the solution for ease)
        initial_parameters = np.array([25.1, 3.1, 5.1])

        # solve inverse problem
        problem.set_max_unchanged_iterations(iterations=1, threshold=1) # just to make it run quick

        valid_obj_func = [pints.MeanSquaredError, pints.RootMeanSquaredError, pints.SumOfSquaresError]
        for obj_func in valid_obj_func:
            problem.set_objective_function(objective_function=obj_func)
            problem.find_optimal_parameter(initial_parameter=initial_parameters)
            initial_values, model_parameters, _ = problem.get_estimate()

            assert initial_values is not None
            assert model_parameters is not None

    def test_set_optimiser(self):
        """Test whether the set_optimiser method works as expected. The estimated values
        are not of interest but rather whether the optimiser are properly embedded.
        """
        wrapped_model = inference.Myokit2PintsModelWrapper(self.myokit_model)
        problem = inference.SingleOutputInverseProblem(model=wrapped_model,
                                                       times=self.times,
                                                       values=self.data
                                                       )

        # start somewhere in parameter space (close to the solution for ease)
        initial_parameters = np.array([25.1, 3.1, 5.1])

        # solve inverse problem
        problem.set_max_unchanged_iterations(iterations=1, threshold=1) # just to make it run quick

        valid_optimisers = [pints.CMAES, pints.NelderMead, pints.PSO, pints.SNES, pints.XNES]
        for opt in valid_optimisers:
            problem.set_optimiser(optimiser=opt)
            problem.find_optimal_parameter(initial_parameter=initial_parameters)
            initial_values, model_parameters, _ = problem.get_estimate()

            assert initial_values is not None
            assert model_parameters is not None