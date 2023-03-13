import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit, SubCircuitFactory

from PySpice.Unit import *
import pint
u = pint.UnitRegistry()

resistance = 10*u.kiloohm
print(resistance.units)

circuit = Circuit('Resistor Bridge')

circuit.V('input', 1, circuit.gnd, 10*u.V)
circuit.R(1, 1, 2, 2*u.kiloohm)
circuit.R(2, 1, 3, 1*u.kiloohm)
circuit.R(3, 2, circuit.gnd, 1*u.kiloohm)
circuit.R(4, 3, circuit.gnd, 1*u.kiloohm)
circuit.R(5, 3, 2, 2*u.kiloohm)

print(circuit)