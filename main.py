import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Unit import *

#####################################

from tqdm import tqdm
import csv
import atexit

#####################################

from subcircuit_def import SubCircuitDictionaries
from circuit_analysis import *
from graphing import *
from simulated_annealing import run_walk, final_run_walk
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
    trans = {"LO" :"ZTX107-LO", "HI" : "ZTX107-HI"} #{"NOM" : "ZTX107-NOM"}
    
    sub_dicts = SubCircuitDictionaries()
    fb_dict = sub_dicts.get_feedbackamp_dict(trans)

    fb_dict_better, _ = final_run_walk(fb_dict, 0.00001, k=5000)

    kMax = 10
    numWalk = 1
    Tinit = 10/np.log(1/0.45-1)

    print("Running Simulated Annealing...")
    with tqdm(total=kMax*numWalk) as pbar:
        for i in range(numWalk):
            sbest, ebest = run_walk(T=Tinit, kMax=kMax, s_0=fb_dict_better, pbar=pbar)
            sbest_list.append(sbest)
            ebest_list.append(ebest)
    
    print(sbest_list[np.argmin(ebest_list)])
    print(f'Ebest: {min(ebest_list):0.2E}')
    print("Running Greedy Walk...")
    sbest, ebest = final_run_walk(sbest_list[np.argmin(ebest_list)], min(ebest_list), k=5000)
    print(sbest)
    sbest_list.append(sbest)
    ebest_list.append(ebest)
    sbest_analyser = CircuitAnalyzer(sbest)
    sstart_analyser = CircuitAnalyzer(fb_dict)
    print(f"Best: BW: {sbest_analyser.BW:.2E}, Gain: {sbest_analyser.DC_gain:.2E}, Current: {sbest_analyser.OP_current:.2E}")#, Goodness: {sbest_analyser.goodness:.2E}")
    print(f"Start BW: {sstart_analyser.BW:.2E}, Gain: {sstart_analyser.DC_gain:.2E}, Current: {sstart_analyser.OP_current:.2E}")#, Goodness: {sstart_analyser.goodness:.2E}")
    # print(sbest_analyser.OP_current)
    make_bode_plot(sbest_analyser.get_AC_analysis())

    plt.scatter([i for i in range(len(mega_goodness))],mega_goodness)
    plt.show()

    make_bode_plot_from_list([sstart_analyser.get_AC_analysis(), sbest_analyser.get_AC_analysis()]) 

    # norm_dist = [np.sqrt(np.sum([(s_curr[key]/fb_dict[key] - 1)**2 for key in free_vars])) for s_curr in sbest_list]
    # make_2d_plot(norm_dist, [-e_i for e_i in ebest_list])



    

