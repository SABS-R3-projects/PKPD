import unittest
from PKPD.model import model
import matplotlib.pyplot as plt
import numpy as np
import os


class TestModel(unittest.TestCase):

    # file_name = 'PKPD/mmt/one_compartment.mmt'
    file_name = '../../PKPD/mmt/one_compartment.mmt'
    models = model.Model()

    def setUp(self) -> None:
        self.models.mmtfile = '../../PKPD/mmt/one_compartment.mmt'
        self.models.read_mmt_file()

    def test_read_mmt_file(self):
        self.assertTrue(self.models.initial_values)
        self.assertTrue(self.models.central_compartment_name)
        self.assertEqual(self.models.dimension, len(self.models.initial_values))
        self.assertTrue(type(self.models.params) is dict)

    def test_set_mmt_file(self):
        self.models.set_mmt_file('test')
        self.assertTrue(self.models.mmtfile == 'test')

    def test_set_initial_values(self):
        pass

    def test_set_model(self):
        pass

    def test_set_protocol(self):
        pass
        #model.set_protocol()


    def test_set_params(self):
        qname = 'param.CL'
        value = 4.0
        self.models.set_params(CL = value)
        self.assertEqual(self.models.model.get(qname).eval(), value)

    def test_get_mmt_file(self):
        pass

    def test_get_initial_values(self):
        pass

    def test_get_model(self):
        pass

    def test_get_protocol(self):
        pass

    def test_get_params(self):
        param_dict = {'param.CL': 3, 'param.V_c' : 5}
        self.assertEqual(param_dict, self.models.get_params())

    def test_solve(self):
        #Checks Max Error Pre Spike < 1e-8
        t = np.linspace(0.0, 24.0, 1000)
        self.models.set_initial_values([25.0])
        self.models.solve(25.0, log_times=t)
        CL = self.models.params['param.CL']
        Vc = self.models.params['param.V_c']
        y = sum([25 * np.heaviside(t - 8.0 * i, 1) * np.exp(-CL * (t - 8.0 * i) / Vc) for i in range(0, 4)])
        #y = 25.0*np.exp(-CL*t/Vc)
        solution = self.models.get_solution()
        plt.figure(1)
        plt.title('Numerical and Exact Solution')
        plt.plot(solution['engine.time'], solution['bolus.y_c'], 'x')
        plt.plot(t, y)
        plt.legend(['Numerical', 'Exact'])
        plt.show()
        error = np.abs(y - solution['bolus.y_c'])
        plt.figure(2)
        plt.title('Solution Error [Heaviside spikes]')
        plt.plot(t, error)
        plt.show()
        self.assertLess(np.max(error[:330]), 1e-8)

    def test_get_solution(self):
        pass
