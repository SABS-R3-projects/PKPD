import unittest
from PKPD.models import model_class
import matplotlib.pyplot as plt
import numpy as np

class TestModel(unittest.TestCase):
    #file_name = 'PKPD/mmt/one_compartment.mmt'
    file_name = '../../PKPD/mmt/one_compartment.mmt'
    model = model_class.Model(file_name)
