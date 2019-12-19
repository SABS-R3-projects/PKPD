import unittest

import myokit
import numpy as np

from PKPD.model import model as m



class TestModel(unittest.TestCase):
    """Tests the functionality of all methods of the Model class.
    """
    # Test case I: 1-compartment model
    file_name = 'PKPD/mmt/one_compartment.mmt'
    one_comp_model = m.SingleOutputModel(file_name)

    def test_init(self):
        """Tests whether the Model class initialises as expected.
        """
        # Test case I: 1-compartment model
        ## expected:
        state_name = 'bolus.y_c'
        parameter_names = ['param.CL', 'param.V_c']
        number_model_parameters = 2
        number_parameters_to_fit = 3

        ## assert initilised values coincide
        assert state_name == self.one_comp_model.state_name
        for parameter_id, parameter in enumerate(self.one_comp_model.parameter_names):
            assert parameter_names[parameter_id] == parameter
        assert number_model_parameters == self.one_comp_model.number_model_parameters
        assert number_parameters_to_fit == self.one_comp_model.number_parameters_to_fit

    def test_n_parameters(self):
        """Tests whether the n_parameter method returns the correct number of fit parameters.
        """
        # Test case I: 1-compartment model
        ## expected
        n_parameters = 3

        ## assert correct number of parameters is returned.
        assert n_parameters == self.one_comp_model.n_parameters()

    def test_n_outputs(self):
        """Tests whether the n_outputs method returns the correct number of outputs.
        """
        # Test case I: 1-compartment model
        ## expected
        n_outputs = 1

        ## assert correct number of outputs.
        assert n_outputs == self.one_comp_model.n_outputs()

    def test_simulate(self):
        """Tests whether the simulate method works as expected. Tests implicitly also whether
        the _set_parameters method works properly.
        """
        # Test case I: 1-compartment model
        parameters = [20, 2, 4] # different from initialsed parameters
        times = np.arange(25)

        ## expected
        model, protocol, _ = myokit.load(self.file_name)
        model.set_state([parameters[0]])
        model.set_value('param.CL', parameters[1])
        model.set_value('param.V_c', parameters[2])
        simulation = myokit.Simulation(model, protocol)
        myokit_result = simulation.run(duration=times[-1]+1, log=['bolus.y_c'], log_times = times)
        expected_result = myokit_result.get('bolus.y_c')

        ## assert that Model.simulate returns the same result.
        model_result = self.one_comp_model.simulate(parameters, times)

        assert np.array_equal(expected_result, model_result)