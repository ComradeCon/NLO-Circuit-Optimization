import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Unit import *

#####################################

from tqdm import tqdm
import csv
import atexit
import time

#####################################

from subcircuit_def import SubCircuitDictionaries
from circuit_analysis import *
from graphing import *
from simulated_annealing import run_walk, final_run_walk, neighbour, free_vars
from helper_funcs import single

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
    trans = {}
    if single.dBeta:
        trans = {"LO" :"ZTX107-LO", "HI" : "ZTX107-HI"} 
    else:
        trans = {"NOM" : "ZTX107-NOM"} 
    sub_dicts = SubCircuitDictionaries()
    fb_dict = sub_dicts.get_feedbackamp_dict(trans)

    if single.isRand: 
        temp = neighbour(fb_dict, free_vars, 10)
        gain_start = CircuitAnalyzer(temp).DC_gain
        while(gain_start > 944 or gain_start < 400): # randomize within bounds
            temp = neighbour(fb_dict, free_vars, 10)
            gain_start = CircuitAnalyzer(temp).DC_gain
        fb_dict = temp

    v = single.isVerbose
    kMax = single.kAnnealing
    numWalk = single.nWalk
    Tinit = single.T

    startSA = time.time()
    if v:
        if single.isRand and single.isVerbose:
            make_bode_plot(CircuitAnalyzer(fb_dict).get_AC_analysis())
        print("Running Simulated Annealing in Verbose Mode...")
        for i in range(numWalk):
            print(f"Walk #{i+1}...")
            sbest, ebest = run_walk(T=Tinit, kMax=kMax, s_0=fb_dict)
            sbest_list.append(sbest)
            ebest_list.append(ebest)
    else:
        print("Running Simulated Annealing...")
        with tqdm(total=kMax*numWalk) as pbar:
            for i in range(numWalk):
                sbest, ebest = run_walk(T=Tinit, kMax=kMax, s_0=fb_dict, pbar=pbar)
                sbest_list.append(sbest)
                ebest_list.append(ebest)
    endSA = time.time()
    if v:
        print(f'Simulated Annealing Ebest: {min(ebest_list):0.2E}')
        print()
    print("Running Greedy Walk...")
    sbest, ebest = final_run_walk(fb_dict, k=single.kGreedy)
    print()
    endGRW = time.time()
    sGRW_analyser = CircuitAnalyzer(sbest)
    sSA_analyser = CircuitAnalyzer(sbest_list[np.argmin(ebest_list)])
    sstart_analyser = CircuitAnalyzer(fb_dict)
    print(f"        Neigbour SD: {single.sigma:.2}")
    print(f"           SA Steps: {kMax}, SA Walks: {numWalk}, Temp: {single.T}")
    print(f"          GRW Steps: {single.kGreedy}")
    print(f"    Check Trans Tol: {single.dBeta}")
    print()
    print(f"               Goal: BW:>{7.2*10**6:.2E}, Gain:~{1000:.2E}, Current:<{0.012:.2E}")
    print(f"              Start: BW: {sstart_analyser.BW:.2E}, Gain: {sstart_analyser.DC_gain:.2E}, Current: {sstart_analyser.OP_current:.2E}")
    print(f"Simulated Annealing: BW: {sSA_analyser.BW:.2E}, Gain: {sSA_analyser.DC_gain:.2E}, Current: {sSA_analyser.OP_current:.2E}, Time: {round(endSA - startSA)}s")
    print(f" Greedy Random Walk: BW: {sGRW_analyser.BW:.2E}, Gain: {sGRW_analyser.DC_gain:.2E}, Current: {sGRW_analyser.OP_current:.2E}, Time: {round(endGRW - endSA)}s")

    make_bode_plot_from_list([sstart_analyser.get_AC_analysis(), sSA_analyser.get_AC_analysis(), sGRW_analyser.get_AC_analysis()]) 

    plt.scatter([i for i in range(len(mega_goodness))],mega_goodness)
    plt.xlabel("Iteration #")
    plt.ylabel("Goodness")
    plt.title("Goodness vs Cummulative Iteration #")
    plt.show()

    sbest_list.append(sbest)
    ebest_list.append(ebest)