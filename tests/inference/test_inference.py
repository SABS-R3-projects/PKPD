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
        duration = times[-1] - times[0]

        state_names = [state.qname() for state in myokit_model.model.states()]

        # Myokit
        myokit_model.solve(duration=duration, log_times=times)

        np_myokit_times = np.array(myokit_model.get_solution('engine.time'))
        print('times: ', np.array(myokit_model.get_solution('engine.time')).shape)
        print('values: ', myokit_model.get_solution(myokit_model.central_compartment_name))
        for state in myokit_model.model.states():
            print(state.qname())
        print('times: ', times[:-1].shape)

        # Wrapped Model
        # something is wring here!!! Continue checking the wrapping and then go on
        # with find optimal values.
        assert np.testing.assert_approx_equal(times[:-1], np_myokit_times)



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
