import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Unit import *

#####################################

from tqdm import tqdm

#####################################

from subcircuit_def import SubCircuitDictionaries, Cascode
from circuit_analysis import *
from graphing import *
from simulated_annealing import run_walk
from timing import tic, toc

#####################################

if __name__ == "__main__":
    # settings
    currTrans = "ZTX107-NOM"
    free_vars = ['RB1','RB2','RB3','RC','RE_deg','RE']
    temp = 25
    
    cascode_dict = get_base_dict(currTrans)

    sbest_list = []
    ebest_list = []

    kMax = 500
    numWalk = 20
    Tinit = 10**6

    with tqdm(total=kMax*numWalk) as pbar:
        for i in range(numWalk):
            sbest, ebest = run_walk(T=Tinit, kMax=kMax, s_0=cascode_dict, free_vars=free_vars, currTrans=currTrans, pbar=pbar)
            sbest_list.append(sbest)
            ebest_list.append(ebest)

    sbest = sbest_list[np.argmin(ebest_list)]
    print(sbest)
    make_bode_plot_from_list([make_analysis(sbest,currTrans),make_analysis(cascode_dict,currTrans)]) 


    # analysis = simulator.operating_point()
    # for node in analysis.branches.values():
    #     print('Node {}: {:5.10f} A'.format(str(node), float(node))) # Fixme: format value + unit

    norm_dist = [np.sqrt(np.sum([(s_curr[key]/cascode_dict[key] - 1)**2 for key in free_vars])) for s_curr in sbest_list]
    make_2d_plot(norm_dist, [-e_i for e_i in ebest_list])

