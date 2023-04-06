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
    def get_cascode1_dict(self) -> dict[str, float | dict[str,str]]:
        return {
            'Cc' : 10**6,
            'RB1' : 100000,
            'RB2' : 12100,
            'RB3' : 21500,
            'RC' : 3010,
            'RE_deg' : 19.6,
            'RE' : 237
        }
        # return {
        #     'Cc' : 10**6,
        #     'RB1' : 10000,
        #     'RB2' : 10000,
        #     'RB3' : 10000,
        #     'RC' : 1000,
        #     'RE_deg' : 10,
        #     'RE' : 100
        # }

    def get_cascode2_dict(self) -> dict[str, float | dict[str,str]]:
        return {
            'Cc' : 10**6,
            'RB1' : 59000,
            'RB2' : 10500,
            'RB3' : 18700,
            'RC' : 1620,
            'RE_deg' : 11.0,
            'RE' : 383
        }
        # return {
        #     'Cc' : 10**6,
        #     'RB1' : 10000,
        #     'RB2' : 10000,
        #     'RB3' : 10000,
        #     'RC' : 1000,
        #     'RE_deg' : 10,
        #     'RE' : 100
        # }
    
    def get_inStage_dict(self) -> dict[str, float | dict[str,str]]:
        return {
            'Cc' : 10**6,
            'RB1' : 205000,
            'RB2' : 51100,
            'RE' : 715
        }
    
    def get_outStage_dict(self) -> dict[str, float | dict[str,str]]:
        return {
            'Cc' : 10**6,
            'RB1' : 147000,
            'RB2' : 365000,
            'RB3' : 147000,
            'RC' : 301,
            'RE' : 110
        }

    def get_feedbackamp_dict(self, trans):
        return {
            'cascode1' : self.get_cascode1_dict(),
            'cascode2' : self.get_cascode2_dict(),
            'inStage' : self.get_inStage_dict(),
            'outStage' : self.get_outStage_dict(),
            # 'RF' : 30100,
            'RF' : 26100, 
            'trans' : trans
        }

# Cc on input but not output
class Cascode1(SubCircuitFactory):
    NODES = ('Vcc','gnd','in_node','out','VE')
    NAME = 'cascode1'
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

# Cc on input but not output
class Cascode2(SubCircuitFactory):
    NODES = ('Vcc','gnd','in_node','out')
    NAME = 'cascode2'
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

class GainStage(SubCircuitFactory):
    NODES = ('Vcc','gnd','in_node','out','FB_in')
    NAME = 'gainStage'
    def __init__(self, gainDict : dict[str, float | dict[str, str]], trans : str):
        super().__init__()
        self.subcircuit(Cascode1(gainDict['cascode1'], trans))
        self.X('cascode_1','cascode1','Vcc', 'gnd','in_node','gain_int','FB_in')
        self.subcircuit(Cascode2(gainDict['cascode2'], trans))
        self.X('cascode_2','cascode2','Vcc', 'gnd','gain_int','out')

# Cc on input but not output
class InputStage(SubCircuitFactory):
    NODES = ('Vcc','gnd','in_node','out')
    NAME = 'inStage'
    def __init__(self, inputDict : dict[str, float | dict[str, str]], trans : str):
        super().__init__()
        # Input Cap
        self.C('Cc1','in_node','VB', inputDict['Cc']@u_uF)
        # bias resistors
        self.R('RB1', 'Vcc', 'VB', inputDict['RB1']@u_Ω)
        self.R('RB2', 'VB', 'gnd', inputDict['RB2']@u_Ω)
        # transistor 
        self.BJT('Q1','Vcc','VB','out',model=trans) # type: ignore
        self.R('RE','out','gnd',inputDict['RE']@u_Ω)

# Cc on input but not output
class OutStage(SubCircuitFactory):
    NODES = ('Vcc','gnd','in_node','out')
    NAME = 'outStage'
    def __init__(self, outDict : dict[str, float | dict[str, str]], trans : str):
        super().__init__()
        # bias resistors
        self.R('RB1','Vcc','VB1',outDict['RB1']@u_Ω)
        self.R('RB2','VB1','VB2',outDict['RB2']@u_Ω)
        self.R('RB3','VB2','gnd',outDict['RB3']@u_Ω)
        # bias Cc
        self.C('Cc1','in_node','VB2', outDict['Cc']@u_uF)
        self.C('Cc2','gnd','VB1', outDict['Cc']@u_uF)
        # transistors
        self.R('RC','Vcc','out',outDict['RC']@u_Ω)
        self.BJT('Q1','out','VB1','VC',model=trans) # type: ignore
        self.BJT('Q2','VC','VB2','VE',model=trans) # type: ignore
        self.R('RE','VE','gnd',outDict['RE']@u_Ω)

# Cc on input but not output
class FeedBackAmp(SubCircuitFactory):
    NAME = 'feedbackamp'
    NODES = ('Vcc','gnd','in_node','out')
    def __init__(self, fbDict : dict, trans : str):
        super().__init__()
        # Input Stage
        self.subcircuit(InputStage(fbDict['inStage'], trans))
        self.X('in_Stage','inStage','Vcc','gnd','in_node','gain_in')
        # Gain Stages
        self.subcircuit(GainStage(fbDict,trans))
        self.X('gain_Stage','gainStage','Vcc','gnd','gain_in','gain_out','FB_in')
        self.R('RF','gain_out','FB_in',fbDict['RF']@u_Ω)
        # Output Stage
        self.subcircuit(OutStage(fbDict['outStage'], trans))
        self.X('out_stage','outStage','Vcc','gnd','gain_out','out')



def get_base_circuit() -> Circuit:
    # circuit setup
    circuit = Circuit('main')
    
    # general circuit definition 
    circuit.V('VDC', 'Vcc', circuit.gnd, 9@u_V)
    circuit.C('Cc_load','out','AC_out', 1@u_F) 
    return circuit