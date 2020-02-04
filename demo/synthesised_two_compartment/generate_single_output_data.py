"""Generates time-series drug concentration data in central compartment based on .2comp_subct_linear.mmt and saves it to .csv file.
"""
import numpy as np
import pandas as pd

from PKPD.model import model as m
from PKPD.inference import inference

# generating data
file_name = 'demo/synthesised_two_compartment/2comp_subcut_linear.mmt'
model = m.SingleOutputModel(file_name)

# List of parameters: ['centralCompartment.drug', 'doseCompartment.drug', 'peripheralCompartment.drug', 'centralCompartment.CL',
# 'centralCompartment.Kcp', 'centralCompartment.V', 'doseCompartment.Ka', 'peripheralCompartment.Kpc', 'peripheralCompartment.V']
true_parameters = [0, 0, 0, 1, 3, 5, 2, 2, 2]

times = np.linspace(0.0, 24.0, 100)
model_result = model.simulate(true_parameters, times)

# add white noise to generate data
scale = np.mean(model_result) * 0.05 # arbitrary choice of noise (not too much, not too little)
data = model_result + np.random.normal(loc=0.0,
                                       scale=scale,
                                       size=len(model_result)
)

df = pd.DataFrame({'time_h': times, 'concentration_ng_mL': data})
df.to_csv('demo/synthesised_two_compartment/two_compartment_single_output.csv', index=False)

