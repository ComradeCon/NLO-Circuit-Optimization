import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Unit import *

#####################################

from tqdm import tqdm
import csv
import atexit

#####################################

from subcircuit_def import SubCircuitDictionaries, Cascode
from circuit_analysis import *
from graphing import *
from simulated_annealing import run_walk
import helper_funcs

#####################################
    
sbest_list = []
ebest_list = []

def capture_data():
    with open('data.csv', mode='w') as data:
        data = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for e, s in zip(ebest_list, sbest_list):
            data.writerow([-e,s])
            
atexit.register(capture_data)

if __name__ == "__main__":
    # settings
    trans = {"LO" :"ZTX107-LO", "NOM" : "ZTX107-NOM", "HI" : "ZTX107-HI"}
    free_vars = ['RB1','RB2','RB3','RC','RE_deg','RE']
    temp = 25
    
    sub_dicts = SubCircuitDictionaries()
    cascode_dict = sub_dicts.get_cascode_dict(trans)

    kMax = 500
    numWalk = 1
    Tinit = 250

    with tqdm(total=kMax*numWalk) as pbar:
        for i in range(numWalk):
            sbest, ebest = run_walk(T=Tinit, kMax=kMax, s_0=cascode_dict, free_vars=free_vars, pbar=pbar)
            sbest_list.append(sbest)
            ebest_list.append(ebest)

    sbest = sbest_list[np.argmin(ebest_list)]
    print(sbest)
    print(min(ebest_list))
    sbest_analyser = CircuitAnalyzer(sbest)
    print(sbest_analyser.OP_current)
    make_bode_plot_from_list([sbest_analyser.get_AC_analysis(), CircuitAnalyzer(cascode_dict).get_AC_analysis()]) 

    norm_dist = [np.sqrt(np.sum([(s_curr[key]/cascode_dict[key] - 1)**2 for key in free_vars])) for s_curr in sbest_list]
    make_2d_plot(norm_dist, [-e_i for e_i in ebest_list])



    

