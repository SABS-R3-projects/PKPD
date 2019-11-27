import unittest
from PKPD.model import model
import matplotlib.pyplot as plt
import myokit
import numpy as np
import os


class TestModel(unittest.TestCase):

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

    def test_set_get_mmt_file(self):
        self.models.set_mmt_file('test')
        self.assertTrue(self.models.mmtfile == 'test')
        self.assertEqual(self.models.get_mmt_file(), 'test')

    def test_set_get_initial_values(self):
        vals = self.models.get_initial_values()
        new_vals = list(range(0,len(vals)))
        self.models.set_initial_values(new_vals)
        self.assertEqual(self.models.initial_values, new_vals)
        self.assertEqual(self.models.model.state(), new_vals)

    def test_set_get_model(self):
        self.assertTrue(type(self.models.model) == myokit._model_api.Model)
        self.assertEqual([n.qname() for n in self.models._get_model().variables()], [n.qname() for n in myokit.load(self.models.mmtfile)[0].variables()])

    def test_set_get_protocol(self):
        #self.models.set_protocol('model.mmt')
        #self.assertTrue(print(self.models.protocol) == '[[protocol]]\n# Level  Start    Length   Period   Multiplier\n1.0      0.0      0.1      0.0      0')
        pass #not required yet

    def test_set_get_params(self):
        qname = 'param.CL'
        value = 4.0
        self.models.set_params(CL = value)
        self.assertEqual(self.models.model.get(qname).eval(), value)
        param_dict = {'param.CL': 4.0, 'param.V_c' : 5.0}
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
        solution_t = self.models.get_solution('engine.time')
        solution_y = self.models.get_solution(self.models.central_compartment_name)
        plt.figure(1)
        plt.title('Numerical and Exact Solution')
        plt.plot(solution_t, solution_y, 'x')
        plt.plot(t, y)
        plt.legend(['Numerical', 'Exact'])
        plt.show()
        error = np.abs(y - solution_y)
        plt.figure(2)
        plt.title('Solution Error [Heaviside spikes]')
        plt.plot(t, error)
        plt.show()
        self.assertLess(np.max(error[:330]), 1e-8)

