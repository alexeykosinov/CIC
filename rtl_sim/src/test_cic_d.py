import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer
from cocotb.triggers import RisingEdge, ReadOnly
from fixedpoint import FixedPoint
from collections import deque

import random
import warnings
import os
import logging
import cocotb_test.simulator
import pytest

import importlib.util

CLK_PERIOD_NS = 100

class TB(object):
    def __init__(self,dut):
        random.seed(30) # reproducible tests
        self.dut = dut
        self.R = dut.CIC_R
        self.M = dut.CIC_M
        self.N = dut.CIC_N
        self.INP_DW = dut.INP_DW
        self.OUT_DW = dut.OUT_DW
        self.SMALL_FOOTPRINT = dut.SMALL_FOOTPRINT

        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)        
        
        tests_dir = os.path.abspath(os.path.dirname(__file__))
        model_dir = os.path.abspath(os.path.join(tests_dir, 'cic_d_model.py'))
        spec = importlib.util.spec_from_file_location("cic_d_model", model_dir)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        self.model = foo.Model(self.R, self.M, self.N, self.INP_DW, self.OUT_DW) 
        
        cocotb.fork(Clock(dut.clk, CLK_PERIOD_NS, units='ns').start())
        
        
    async def cycle_reset(self):
        self.dut.reset_n.setimmediatevalue(1)
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.reset_n <= 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.reset_n <= 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        
@cocotb.test()
async def simple_test_(dut):
    tb = TB(dut)
    tb.dut.clear <= 0
    await tb.cycle_reset()
    for i in range(10):
        await RisingEdge(dut.clk)
        tb.dut.inp_samp_str <= 1
        tb.dut.inp_samp_data <= i
    tb.dut.inp_samp_str <= 0
    await RisingEdge(dut.clk)
    
# cocotb-test


tests_dir = os.path.abspath(os.path.dirname(__file__))
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'rtl', 'verilog'))

@pytest.mark.parametrize("R", [100])
@pytest.mark.parametrize("N", [10])
@pytest.mark.parametrize("M", [1])
@pytest.mark.parametrize("INP_DW", [16])
@pytest.mark.parametrize("OUT_DW", [16])
@pytest.mark.parametrize("SMALL_FOOTPRINT", [0])
def test_cic_d(request, R, N, M, INP_DW, OUT_DW, SMALL_FOOTPRINT):
    dut = "cic_d"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.sv"),
        os.path.join(rtl_dir, "comb.sv"),
        os.path.join(rtl_dir, "integrator.sv"),
        os.path.join(rtl_dir, "downsampler.sv"),
    ]
    includes = [
        os.path.join(rtl_dir, ""),
        os.path.join(rtl_dir, "cic_functions.vh"),
    ]    

    parameters = {}

    parameters['CIC_R'] = R
    parameters['CIC_N'] = N
    parameters['CIC_M'] = M
    parameters['INP_DW'] = INP_DW
    parameters['OUT_DW'] = OUT_DW
    parameters['SMALL_FOOTPRINT'] = SMALL_FOOTPRINT

    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}
    sim_build="sim_build/" + "_".join(("{}={}".format(*i) for i in parameters.items()))
    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
        includes=includes,
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
    )
    
