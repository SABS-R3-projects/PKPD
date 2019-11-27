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
        self.models.mmtfile = 'test'
        self.models.set_mmt_file()
        self.assertTrue(self.models.mmtfile == 'test')

    def test_set_initial_values(self, initial_values):
        pass

    def test_set_model(self):
        pass

    def test_set_protocol(self, protocol):
        pass

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
        pass

    def test_get_solution(self):
        pass
