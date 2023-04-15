import numpy as np

##########################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.NgSpice.Simulation import NgSpiceSharedCircuitSimulator
from PySpice.Unit import *

##########################################

from subcircuit_def import *

# records every valid goodness value
mega_goodness = []

# grabs the transistor paths
dicts = SubCircuitDictionaries()
trans_dict = dicts.get_trans_dict()

# takes in a circuit definition (state) and calculates goodness
class CircuitAnalyzer: 
    def __init__(self, curr_dict : dict[str, float | dict[str,str]]) -> None:
        self.curr_dict = curr_dict
        # PySpice circuit from input dictionary
        self.circuits = self.__make_circuit() 
        # creates simulators for each transistor tolerance
        self.simulators = self.__make_simulator() 
        # DC simulation of circuit
        self.__DC_analyses = self.__make_DC_analysis()
        # extracts the operating current 
        self.OP_current = self.__get_OP_current()
        # calculates punishment for current usage
        self.OP_current_goodness = max(min(1,1 if self.OP_current <= 0.01 else 1-(100*(self.OP_current-0.01))**2),0.001)
        if (self.OP_current_goodness > 0.5): # rejects high current circuits
            # AC simulation 
            self.__AC_analyses = self.__make_AC_analysis()
            self.frequencies = dict()
            self.gains = dict()
            # grabs the frequency and gain data from the analysis
            for key, value in self.__AC_analyses.items():
                self.frequencies[key] = value.frequency
                self.gains[key] = np.absolute(value.AC_out)
            # calculates & punishes the bandwidth 
            self.BW, self.DC_gain, self.key_min = self.__get_BW()
            # calculates goodness (higher better)
            self.goodness = self.__get_goodness()
            # records valid goodness
            mega_goodness.append(self.goodness)
        else: # rejected circuit
            self.BW = 0
            self.DC_gain = 0
            self.goodness = -1
    
    # creates the circuit using the PySpice environment 
    def __make_circuit(self) -> dict[str, Circuit]:
        circuits = {}
        for key, value in self.curr_dict['trans'].items(): # type: ignore
            circuit = get_base_circuit()
            circuit.SinusoidalVoltageSource('AC_voltage', 'ac_in', circuit.gnd, amplitude=1@u_V) 
            circuit.R('RAC', 'ac_in', 'in_node', 1500@u_Ohm)
            circuit.include(trans_dict[value])
            circuit.subcircuit(FeedBackAmp(self.curr_dict, value))
            circuit.X('fbamp1','feedbackamp','Vcc', circuit.gnd,'in_node','out')
            circuits[key] = circuit
        return circuits

    # creates simulator objects for each transistor tolerance
    def __make_simulator(self, temperature = 25) -> dict[str, NgSpiceSharedCircuitSimulator]:
        simulators = dict()
        for key, value in self.circuits.items():
            temp = value.simulator(temperature=temperature, nominal_temperature=temperature)
            temp.save(["AC_out","i(vvdc)"])
            simulators[key] = temp
        return simulators

    # calculates DC operating point of the circuit
    def __make_DC_analysis(self) -> dict:
        DC_analyses = dict()
        for key, value in self.simulators.items():
            DC_analyses[key] = value.operating_point()
        return DC_analyses

    # returns the max current draw of all the transistor tolerances
    def __get_OP_current(self) -> float:
        return max(max([abs(float(np.absolute(x[0]))) for x in DC_analysis.branches.values()]) for DC_analysis in self.__DC_analyses.values())

    # simulates the circuit between a range of frequencies on a log scale
    def __make_AC_analysis(self) -> dict:
        AC_analyses = dict()
        for key, value in self.simulators.items():
            AC_analyses[key] = value.ac(start_frequency=1@u_kHz, stop_frequency=100@u_MHz, number_of_points=50,  variation='dec')
        return AC_analyses
    
    # calculates the 1.5dB bandwidth and punishes bandwidth for being out of the desired gain range
    def __get_BW(self) -> tuple[float, float, str]:
        BW_min = None
        DC_gain_min = None
        key_min = ""
        for key, freq in self.frequencies.items():
            DC_gain_curr = self.gains[key][0].value
            if DC_gain_curr > 100: # only check minimum operational amplifiers 
                index_3dB = None
                for i, x in enumerate(self.gains[key]):
                    if x.value > 1188.5 or x.value < 944: # finds the 60+-1.5dB BW
                        index_3dB = i
                        break
                if index_3dB > 1: # if its valid, approximates the exact value
                    currBW = self.__lin_approx(freq[index_3dB].value,self.gains[key][index_3dB],freq[index_3dB-1].value,self.gains[key][index_3dB-1], DC_gain_curr*0.944)
                else: # invalid -> needs to be punished
                    if index_3dB == 0:
                        for i, x in enumerate(self.gains[key]):
                            # finds 1.5dB bandwidth
                            if x.value <= DC_gain_curr*0.944 or x.value >= DC_gain_curr/0.944: 
                                index_3dB = i
                                break
                        # approximates exact value
                        currBW = self.__lin_approx(freq[index_3dB].value,self.gains[key][index_3dB],freq[index_3dB-1].value,self.gains[key][index_3dB-1], DC_gain_curr*0.944)
                        i = 0
                        adj = 0
                        # punishes bandwidth based on mean square distance from desired gain
                        while(freq[i].value < 7.2*10**6): 
                            adj += min((self.gains[key][i].value - 1188.5)**2,(self.gains[key][i].value - 944)**2)
                            i += 1
                        currBW /= np.sqrt(adj)/i
                # boot strapping and takes lower of BWs
                if index_3dB != None and currBW != None and (BW_min == None or currBW < BW_min):
                    BW_min = currBW 
                    DC_gain_min = DC_gain_curr
                    key_min = key
        return (lambda: (BW_min, DC_gain_min, key_min), lambda: (0,0,self.curr_dict['trans'][list(self.curr_dict['trans'].keys())[0]]))[BW_min == None]() 

    # simple linear approximation
    def __lin_approx(self, x1, y1, x2, y2, y_target):
        return (y_target-y1)*(x2-x1)/(y2-y1) + x1

    # unused
    def __get_GBWP(self) -> float:
        return self.BW*self.DC_gain

    # calculates goodness
    def __get_goodness(self) -> float: 
        goodness = self.BW*self.OP_current_goodness
        if goodness > 0:
            return goodness
        else:
            return 0
    
    # returns analysis for worst case of transistor tolerance
    def get_AC_analysis(self):
        return self.__AC_analyses[self.key_min]