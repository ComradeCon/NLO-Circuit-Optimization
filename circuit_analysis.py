import numpy as np

##########################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Simulation import CircuitSimulator
from PySpice.Unit import *

##########################################

from subcircuit_def import *

'''
Goals:
- calculate gain bandwidth product
- calculate power draw 
- check if circuit breaks design rules
'''

dicts = SubCircuitDictionaries()
trans_dict = dicts.get_trans_dict()

class CircuitAnalyzer:
    def __init__(self, curr_dict : dict[str, float | dict[str,str]]) -> None:
        self.curr_dict = curr_dict
        self.circuits = self.__make_circuit()
        self.simulators = self.__make_simulator()
        # DC analysis
        self.DC_analyses = self.__make_DC_analysis()
        self.OP_current = self.__get_OP_current()
        # AC analysis
        self.__AC_analyses = self.__make_AC_analysis()
        self.frequencies = dict()
        self.gains = dict()
        for key, value in self.__AC_analyses.items():
            self.frequencies[key] = value.frequency
            self.gains[key] = 20*np.log10([x.value for x in np.absolute(value.AC_out)])
        self.BW, self.key_min, self.mid_gain = self.__get_BW()
        self.GBWP = self.__get_GBWP()
        self.goodness = self.__get_goodness()
    
    def __make_circuit(self) -> dict[str, Circuit]:
        circuits = {}
        for key, value in self.curr_dict['trans'].items(): # type: ignore
            circuit = get_base_circuit()
            circuit.SinusoidalVoltageSource('AC_voltage', 'in_node', circuit.gnd, amplitude=0.1@u_V)
            circuit.include(trans_dict[value])
            circuit.subcircuit(Cascode(self.curr_dict, value))
            circuit.X('cascode1','cascode','Vcc', circuit.gnd,'in_node','out')
            circuits[key] = circuit
        return circuits

    def __make_simulator(self, temp=25) -> dict[str, CircuitSimulator]:
        simulators = dict()
        for key, value in self.circuits.items():
            simulators[key] = value.simulator(temperature=temp, nominal_temperature=temp)
        return simulators

    def __make_DC_analysis(self) -> dict:
        DC_analyses = dict()
        for key, value in self.simulators.items():
            DC_analyses[key] = value.operating_point()
        return DC_analyses

    def __get_OP_current(self) -> float:
        return max(max([abs(float(x)) for x in DC_analysis.branches.values()]) for DC_analysis in self.DC_analyses.values())

    def __make_AC_analysis(self) -> dict:
        AC_analyses = dict()
        for key, value in self.simulators.items():
            AC_analyses[key] = value.ac(start_frequency=1@u_kHz, stop_frequency=200@u_MHz, number_of_points=4,  variation='dec')
        return AC_analyses
    
    # slow, very dumb slow
    def __get_working_range(self, pm_range_db = 3) -> tuple[dict[str, list[list[float]]], dict[str, float]]:
        ranges = dict()
        mid_gains = dict()
        for key, freq in self.frequencies.items():
            all_ranges = [[[fre.value,gain] for fre, gain in zip(freq, self.gains[key]) if (gain > mid - pm_range_db and gain < mid + pm_range_db)] for mid in self.gains[key]]
            index_BW = np.argmax([len(x) for x in all_ranges])
            ranges[key] = all_ranges[index_BW]
            mid_gains[key] = self.gains[key][index_BW]
        return ranges, mid_gains

    def __get_BW(self, pm_range_db = 3) -> tuple[float, str, float]:
        temp, mid_gains = self.__get_working_range(pm_range_db=pm_range_db)
    
        key_min = ''
        value_min = np.inf
        for key, value in temp.items():
            curr_BW = value[-1][0] - value[0][0]
            if curr_BW < value_min:
                key_min = key
                value_min = curr_BW

        return value_min, key_min, mid_gains[key_min]

    def __get_GBWP(self) -> float:
        return self.mid_gain*self.BW

    def __get_goodness(self) -> float: # blows up below 1mA
        return self.GBWP/(self.OP_current + np.exp(1/self.OP_current - 1000))
    
    def get_AC_analysis(self):
        return self.__AC_analyses[self.key_min]

    