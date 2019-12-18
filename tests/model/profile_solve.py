"""Example script to profile the solve method.

Execution:
    - Go to terminal and cd into the PKPD directory.
    - Profile the script by running
        python -m cProfile -o tests/model/profile_solve tests/model/profile_solve.py

Analysis:
    The ouput file can be analysed in a python shell with the pstats module. E.g.
    - import pstats
      p = pstats.Stats('tests/model/profile_solve')
      p.sort_stats('cumulative').print_stats(50)

    prints the 50 functions which consume the most time while executing the script (This includes subfunctions, see documentation https://docs.python.org/2/library/profile.html).
"""

import numpy as np

from PKPD.model.model import Model

# intialise model
file_name = 'PKPD/mmt/one_compartment.mmt'

model = Model()
model.mmtfile = file_name
model.read_mmt_file()

# solve model
t = np.linspace(0.0, 24.0, 10000)
model.solve(25.0, log_times=t)
solution_y = model.get_solution(model.central_compartment_name)