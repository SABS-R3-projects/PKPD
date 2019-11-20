import unittest
from PKPD.model import model
import matplotlib.pyplot as plt
import numpy as np
import os


class TestModel(unittest.TestCase):
    # file_name = 'PKPD/mmt/one_compartment.mmt'
    file_name = '../../PKPD/mmt/one_compartment.mmt'
    models = model.Model(file_name)

    def test_read_mmt_file(self):
        pass

    def test_set_mmt_file(self):
        pass
        #filename = models.set_mmt_file()
        #self.assertTrue(isinstance(filename, str))
        #self.assertTrue(filename[-4:-1] == '.mmt')
        #self.assertTrue(os.path.exists(filename))

    def test_set_initial_values(self, initial_values):
        pass

    def test_set_model(self):
        pass

    def test_set_protocol(self, protocol):
        pass

    def test_set_params(self, params):
        pass

    def test_get_mmt_file(self):
        pass

    def test_get_initial_values(self):
        pass

    def test_get_model(self):
        pass

    def test_get_protocol(self):
        pass

    def test_get_params(self):
        pass

    def test_solve(self):
        pass

    def test_get_solution(self):
        pass
