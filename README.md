# CIC Filter with Python testbenches

This project is based on https://opencores.org/projects/cic_core_2 by Egor Igragimov and on https://opencores.org/projects/cic_core by Vadim Kotelnikov.

The main additions and changes are
- added variable/programmable downsampling rate
- added programmable pre and post scaling
- optimized pipeline structure of comb section -> has much less delay now
- register pruning calculation outside of hdl code -> great speed up for sim and synth if R is large
- python model for simulation
- unit tests using cocotb and cocotb-test

To run the unit tests install
- python >3.8
- iverilog >1.4
- python modules: cocotb, cocotb_test, pytest, pytest-parallel

and run pytest in the repo directory
```
pytest -v --workers 10
```

# TODO
- add CIC interpolator

# License
for old code from opencores LGPL

for new code GPL


