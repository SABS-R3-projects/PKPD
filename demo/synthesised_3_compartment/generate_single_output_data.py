"""Generates time-series drug concentration data in central compartment based on .2comp_subct_linear.mmt and saves it to .csv file.
"""
import numpy as np
import pandas as pd

from PKPD.model import model as m
from PKPD.inference import inference

# generating data
file_name = 'demo/synthesised_3_compartment/3_bolus_linear.mmt'
model = m.SingleOutputModel(file_name)

# List of parameters
true_parameters = [
    0, # central_compartment.drug
    0, # peripheral_compartment_1.drug
    0, # peripheral_compartment_2.drug
    1, # central_compartment.CL
    3, # central_compartment.Kcp1
    2, # central_compartment.Kcp2
    5, # central_compartment.V
    2, # peripheral_compartment_1.Kpc
    2, # peripheral_compartment_1.V
    2, # peripheral_compartment_2.Kpc
    2 # peripheral_compartment_2.V
]

times = np.linspace(0.0, 24.0, 100)
model_result = model.simulate(true_parameters, times)

# add white noise to generate data
scale = np.mean(model_result) * 0.05 # arbitrary choice of noise (not too much, not too little)
data = model_result + np.random.normal(loc=0.0,
                                       scale=scale,
                                       size=len(model_result)
)

df = pd.DataFrame({'time_h': times, 'concentration_ng_mL': data})
df.to_csv('demo/synthesised_3_compartment/three_compartment_single_output.csv', index=False)
