"""Generates time-series drug concentration data based on .1comp_bolus_linear.mmt and saves it to .csv file.
"""
import numpy as np
import pandas as pd

from PKPD.model import model as m
from PKPD.inference import inference

# generating data
file_name = 'demo/synthesised_one_compartment/1comp_bolus_linear.mmt'
one_comp_model = m.SingleOutputModel(file_name)
true_parameters = [0, 2, 4] # [initial drug, CL, V]

times = np.linspace(0.0, 24.0, 100)
model_result = one_comp_model.simulate(true_parameters, times)

# add white noise to generate data
scale = np.mean(model_result) * 0.05 # arbitrary choice of noise (not too much, not too little)
data = model_result + np.random.normal(loc=0.0,
                                       scale=scale,
                                       size=len(model_result)
)

df = pd.DataFrame({'time_h': times, 'concentration_ng_mL': data})
df.to_csv('demo/synthesised_one_compartment/one_compartment.csv', index=False)

