import unittest
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
    def test_find_optimal_parameter(self):
        # Test case I: One Compartment Model
        file_name = 'PKPD/mmt/one_compartment.mmt'

        self.model = model.Model()
        self.model.mmtfile = file_name
        self.model.read_mmt_file()

        print('')
        print('mmt file: ', self.model.get_mmt_file())
        print('initial values: ', self.model.get_initial_values())
        print('params: ', self.model.get_params())
        print('params: ', self.model.get_params())


        assert True
