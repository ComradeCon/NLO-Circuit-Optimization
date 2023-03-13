import numpy as np

##########################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

##########################################

from subcircuit_def import *

'''
Goals:
- calculate gain bandwidth product
- calculate power draw 
- check if circuit breaks design rules
'''

dicts = SubCircuitDictionaries
trans_dict = dicts.get_trans_dict()

class CircuitAnalyzer:
    def __init__(self, analysis) -> None:
        self.analysis = analysis
        self.frequency=self.analysis.frequency
        self.gain=20*np.log10([x.value for x in np.absolute(self.analysis.AC_out)])
        self.working_range_3db, self.mid_gain = self.__get_working_range()

    def GBWP(self) -> float:
        return (self.mid_gain)*(self.BW().value)
        
    # def PWR(self) -> float:

    # slow, very dumb slow
    def __get_working_range(self, pm_range_db = 3) -> list:
        all_ranges = [[[freq,gain] for freq, gain in zip(self.frequency,self.gain) if (gain > mid - pm_range_db and gain < mid + pm_range_db)] for mid in self.gain]
        index_BW = np.argmax([len(x) for x in all_ranges])
        return all_ranges[index_BW], self.gain[index_BW]


    def BW(self, pm_range_db = 3) -> float:
        if pm_range_db == 3:
            return self.working_range_3db[-1][0] - self.working_range_3db[0][0]
        else:
            working_range = self.__get_working_range(pm_range_db=pm_range_db)
            return working_range[-1][0] - working_range[0][0]


def get_GBWP(curr_dict, currTrans, temp=25):
    return CircuitAnalyzer(make_analysis(curr_dict,currTrans,temp)).GBWP()

def make_analysis(curr_dict, currTrans, temp=25):
    circuit = get_base_circuit()
    circuit.SinusoidalVoltageSource('AC_voltage', 'in_node', circuit.gnd, amplitude=0.1@u_V)
    circuit.include(trans_dict[currTrans])
    circuit.subcircuit(Cascode(curr_dict))
    circuit.X('cascode1','cascode','Vcc', circuit.gnd,'in_node','out')
    simulator = circuit.simulator(temperature=temp, nominal_temperature=temp)
    return simulator.ac(start_frequency=1@u_Hz, stop_frequency=200@u_MHz, number_of_points=10,  variation='dec')
        
