from PySpice.Spice.Netlist import SubCircuitFactory, Circuit
from PySpice.Unit import *

################################################

def check_valid_dict(dictionary : dict):
    for key, value in dictionary.items():
        if type(value) != type("lol") and value < 0:
            raise ValueError(f"{key} has bad value of {value}")

class SubCircuitDictionaries:
    def __init__(self) -> None:
        pass
    
    def get_trans_dict() -> dict:
        return {
            "2N2222A" : "library/2N2222A.lib",
            "ZTX107-NOM" : "library/ZTX107-NOM.lib"
        }

    # resistors in ohms
    # capacitors in micro farads 
    def get_cascode_dict() -> dict:
        return {
            'Cc' : 1,
            'RB1' : -1,
            'RB2' : -1,
            'RB3' : -1,
            'RC' : -1,
            'RE_deg' : 0,
            'RE' : -1,
            'trans_model' : -1
        }

# Cc on input but not output
class Cascode(SubCircuitFactory):
    NAME = 'cascode'
    NODES = ('Vcc','gnd','in_node','out')
    def __init__(self, cascodeDict : dict):
        super().__init__()
        check_valid_dict(cascodeDict)
        # bias resistors
        self.R('RB1','Vcc','VB1',cascodeDict['RB1']@u_Ω)
        self.R('RB2','VB1','VB2',cascodeDict['RB2']@u_Ω)
        self.R('RB3','VB2','gnd',cascodeDict['RB3']@u_Ω)
        # bias Cc
        self.C('Cc1','in_node','VB2', cascodeDict['Cc']@u_uF)
        self.C('Cc2','gnd','VB1', cascodeDict['Cc']@u_uF)
        # transistors
        self.R('RC','Vcc','out',cascodeDict['RC']@u_Ω)
        self.BJT('Q1','out','VB1','VC',model=cascodeDict['trans_model'])
        self.BJT('Q2','VC','VB2','VE',model=cascodeDict['trans_model'])
        self.R('RE_deg','VE','VE2',cascodeDict['RE_deg']@u_Ω)
        self.C('Cc3','VE2','gnd',cascodeDict['Cc']@u_uF)
        self.R('RE','VE2','gnd',cascodeDict['RE']@u_Ω)
        

def get_base_circuit():
    # circuit setup
    circuit = Circuit('main')
    
    # general circuit definition 
    circuit.V('VDC', 'Vcc', circuit.gnd, 9@u_V)
    circuit.C('Cc_load','out','AC_out', 1@u_uF)
    circuit.R('R_load','AC_out',circuit.gnd,2.5@u_kΩ)  
    return circuit

def get_base_dict(currTrans):
    dicts = SubCircuitDictionaries
    cascode_dict = dicts.get_cascode_dict()
    cascode_dict['Cc'] = 1
    cascode_dict['RB1'] = 95300
    cascode_dict['RB2'] = 10500
    cascode_dict['RB3'] = 20500
    cascode_dict['RC'] = 3010
    cascode_dict['RE_deg'] = 24.9
    cascode_dict['RE'] = 226
    cascode_dict['trans_model'] = currTrans

    return cascode_dict