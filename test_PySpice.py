# https://pyspice.fabrice-salvaire.fr/releases/latest/overview.html

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Unit import *

class SubCircuit1(SubCircuitFactory):
    NAME = 'sub_circuit1'
    NODES = ('n1','n2')
    def __init__(self,):
        super().__init__()
        self.R(1, 'n1', 'n2', 1@u_Ω)
        self.R(2, 'n1', 'n2', 2@u_Ω)

circuit = Circuit('test')

C1 = circuit.C(1,0,1,1@u_uF)
circuit.subcircuit(SubCircuit1())
circuit.X('1', 'sub_circuit1', 2, 0)

C1.capacitance = 10@u_F

C1.enabled = False

circuit2 = circuit.clone(title="a clone")

C1 = circuit2.C1.detach()

# print(circuit2)

class ParallelResistor(SubCircuitFactory):
    NAME = 'parallel_resistor'
    NODES = ('n1', 'n2')
    def __init__(self, R1, R2):
        super().__init__()
        self.R(1, 'n1', 'n2', R1)
        self.R(2, 'n1', 'n2', R2)

circuit = Circuit('test')
circuit.subcircuit(ParallelResistor(2@u_Ohm, 3@u_Ohm))
circuit.X('1','parallel_resistor', 1, circuit.gnd)

print(circuit)