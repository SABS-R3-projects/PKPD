"""Generates time-series drug concentration data in central compartment based on .2comp_subct_linear.mmt and saves it to .csv file.
"""
import numpy as np
import pandas as pd

from PKPD.model import model as m
from PKPD.inference import inference

# generating data
file_name = 'demo/synthesised_2_compartment/2comp_subcut_linear.mmt'
model = m.MultiOutputModel(file_name)

# set dimensionality of data
model.set_output_dimension(2)

# List of parameters: ['central_compartment.drug', 'dose_compartment.drug', 'peripheral_compartment.drug', 'central_compartment.CL',
# 'central_compartment.Kcp', 'central_compartment.V', 'dose_compartment.Ka', 'peripheral_compartment.Kpc', 'peripheral_compartment.V']
true_parameters = [0, 0, 0, 1, 3, 5, 2, 2, 2]

times = np.linspace(0.0, 24.0, 100)
model_result = model.simulate(true_parameters, times)

# add white noise to generate data
scale = np.mean(model_result) * 0.05 # arbitrary choice of noise (not too much, not too little)
noise =  np.random.normal(loc=0.0,
                          scale=scale,
                          size=model_result.shape
                          )
data = model_result + noise

df = pd.DataFrame({'time_h': times, 'central_ng_mL': data[:, 0], 'peripheral_ng_mL': data[:, 1]})
df.to_csv('demo/synthesised_two_compartment/two_compartment_multi_output.csv', index=False)

