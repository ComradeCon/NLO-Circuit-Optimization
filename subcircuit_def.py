from PySpice.Spice.Netlist import SubCircuitFactory, Circuit
from PySpice.Unit import *

################################################

# def check_valid_dict(dictionary : dict):
#     for key, value in dictionary.items():
#         if type(value) != type("lol") and value < 0:
#             raise ValueError(f"{key} has bad value of {value}")

class SubCircuitDictionaries:
    def __init__(self) -> None:
        pass
    
    def get_trans_dict(self) -> dict:
        return {
            "2N2222A" : "library/2N2222A.lib",
            "ZTX107-HI" : "library/ZTX107-HI.lib",
            "ZTX107-NOM" : "library/ZTX107-NOM.lib",
            "ZTX107-LO" : "library/ZTX107-LO.lib"
        }

    # resistors in ohms
    # capacitors in micro farads 
    def get_cascode_dict(self, trans : dict[str,str]) -> dict[str, float | dict[str,str]]:
        return {
            'Cc' : 10**6,
            'RB1' : 95300,
            'RB2' : 10500,
            'RB3' : 20500,
            'RC' : 3010,
            'RE_deg' : 24.9,
            'RE' : 226,
            'trans' : trans
        }
        # return {
        #     'Cc' : 10**6,
        #     'RB1' : 10000,
        #     'RB2' : 10000,
        #     'RB3' : 10000,
        #     'RC' : 1000,
        #     'RE_deg' : 10,
        #     'RE' : 100,
        #     'trans' : trans
        # }

# Cc on input but not output
class Cascode(SubCircuitFactory):
    NAME = 'cascode'
    NODES = ('Vcc','gnd','in_node','out')
    def __init__(self, cascodeDict : dict[str, float | dict[str, str]], trans : str):
        super().__init__()
        # check_valid_dict(cascodeDict)
        # bias resistors
        self.R('RB1','Vcc','VB1',cascodeDict['RB1']@u_Ω)
        self.R('RB2','VB1','VB2',cascodeDict['RB2']@u_Ω)
        self.R('RB3','VB2','gnd',cascodeDict['RB3']@u_Ω)
        # bias Cc
        self.C('Cc1','in_node','VB2', cascodeDict['Cc']@u_uF)
        self.C('Cc2','gnd','VB1', cascodeDict['Cc']@u_uF)
        # transistors
        self.R('RC','Vcc','out',cascodeDict['RC']@u_Ω)
        self.BJT('Q1','out','VB1','VC',model=trans) # type: ignore
        self.BJT('Q2','VC','VB2','VE',model=trans) # type: ignore
        self.R('RE_deg','VE','VE2',cascodeDict['RE_deg']@u_Ω)
        self.C('Cc3','VE2','gnd',cascodeDict['Cc']@u_uF)
        self.R('RE','VE2','gnd',cascodeDict['RE']@u_Ω)
        

def get_base_circuit() -> Circuit:
    # circuit setup
    circuit = Circuit('main')
    
    # general circuit definition 
    circuit.V('VDC', 'Vcc', circuit.gnd, 9@u_V)
    circuit.C('Cc_load','out','AC_out', 1@u_uF)
    circuit.R('R_load','AC_out',circuit.gnd, 2500@u_Ω)  
    return circuit