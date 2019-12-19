"""Example script to profile the find_optimal_parameters method.

Execution:
    - Go to terminal and cd into the PKPD directory.
    - Profile the script by running
        python -m cProfile -o tests/inference/profile_find_optimal_parameters tests/inference/profile_find_optimal_parameters.py

Analysis:
    The ouput file can be analysed in a python shell with the pstats module. E.g.
    - import pstats
      p = pstats.Stats('tests/inference/profile_find_optimal_parameters')
      p.sort_stats('cumulative').print_stats(50)

    prints the 50 functions which consume the most time while executing the script (This includes subfunctions, see documentation https://docs.python.org/2/library/profile.html).
"""

import pints
import numpy as np

from PKPD.model import model
from PKPD.inference import inference


## Test case: One Compartment Model
# generating data
file_name = 'PKPD/mmt/one_compartment.mmt'

myokit_model = model.Model()
myokit_model.mmtfile = file_name
myokit_model.read_mmt_file()

times = np.linspace(0.0, 24.0, 10000)
duration = times[-1] - times[0] + 1 # plus 1 to keep final time step

# Solve myokit model
myokit_model.solve(duration=duration, log_times=times)
np_myokit_state_values = np.array(myokit_model.get_solution(myokit_model.central_compartment_name))

# add white noise to generate data
scale = np.mean(np_myokit_state_values) * 0.05 # arbitrary choice of noise (not too much, not too little)
data = np_myokit_state_values + np.random.normal(loc=0.0,
                                                 scale=scale,
                                                 size=len(np_myokit_state_values)
                                                 )

# true initial values and parameters
true_intitial_values = myokit_model.get_initial_values()
true_model_parameters = myokit_model.get_params()

wrapped_model = inference.Myokit2PintsModelWrapper(myokit_model)
problem = inference.SingleOutputInverseProblem(model=wrapped_model,
                                               times=times,
                                               values=data
                                               )

# start somewhere in parameter space (close to the solution for ease)
initial_parameters = np.array([25.1, 3.1, 5.1])

# solve inverse problem
problem.set_max_unchanged_iterations(iterations=10, threshold=1e-4)
problem.find_optimal_parameter(initial_parameter=initial_parameters)
initial_values, model_parameters, _ = problem.get_estimate()
print('initial value: ', initial_values)
print('model parameters: ', model_parameters)