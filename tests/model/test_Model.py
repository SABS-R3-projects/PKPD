import unittest
from PKPD.model import model
import matplotlib.pyplot as plt
import numpy as np
import os


class TestModel(unittest.TestCase):
    # file_name = 'PKPD/mmt/one_compartment.mmt'
    file_name = '../../PKPD/mmt/one_compartment.mmt'
    modelclass = model.Model(file_name)

    def test_read_mmt_file(self):
        pass

    def test_set_mmt_file(self):
        filename = modelclass.set_mmt_file()
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename[-4:-1] == '.mmt')
        self.assertTrue(os.path.exists(filename))

    def test_set_initial_values(self, initial_values):


    def test_set_model(self):


    def test_set_protocol(self, protocol):


    def test_set_params(self, params):


    def test_get_mmt_file(self):


    def test_get_initial_values(self):


    def test_get_model(self):


    def test_get_protocol(self):


    def test_get_params(self):


    def test_solve(self):


    def test_get_solution(self):

