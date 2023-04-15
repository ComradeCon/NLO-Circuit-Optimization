import numpy as np
from PySpice.Unit import *
from circuit_analysis import *
from tqdm import tqdm
from helper_funcs import single

# annealing schedule
def temperature(T, b):
    return T*b

# acceptance function
def P(E_past, E_new, T):
    if(E_new >= -1): # rejects bad energies
        return False
    ratio = E_new/E_past 
    if ratio >= 1: # if E_new is better 
        return True
    if T != 0 and 4 > 100*(1-ratio)/T: # throws out below 2% chance
        return 1/(1 + np.exp(100*(1-ratio)/T)) > np.random.random()
    else:
        return False
    
# specify design variables 
free_vars = ['RF','cascode1','cascode2','outStage']
free_vars_dict = {
    'cascode1' : ['RB1','RB2','RB3','RC','RE_deg','RE'],
    'cascode2' : ['RB1','RB2','RB3','RC','RE_deg','RE'],
    'outStage' : ['RE']
}

# generates a random state near "s"
def neighbour(s, free_vars, sd):
    s_new = s.copy()
    for key in free_vars:
        if type(s[key]) == dict: # recursion to handle sub circuits
            s_new[key] = neighbour(s[key], free_vars=free_vars_dict[key], sd=sd)
        else: # moves each component of the state by a random number of discrete steps
            s_new[key] = iter_resistor(s[key], round(np.random.normal(0,sd)))
    return s_new

# smallest valid 2% resistor values 
valid_res = [10.0, 10.5, 11.0, 11.5, 12.1, 12.7, 13.3, 14.0, 14.7, 15.4, 16.2, 16.9, 17.8, 18.7, 19.6, 20.5, 21.5, 22.6, 23.7, 24.9, 26.1, 27.4, 28.7, 30.1, 31.6, 33.2, 34.8, 36.5, 38.3, 40.2, 42.2, 44.2, 46.4, 48.7, 51.1, 53.6, 56.2, 59.0, 61.9, 64.9, 68.1, 71.5, 75.0, 78.7, 82.5, 86.6, 90.9, 95.3]
len_valid_res = len(valid_res)

# changes the resistor value by a given number of steps up or down
def iter_resistor(R,n):
    if n == 0: # no change
        return R

    # extract order of magnitude 
    OOM = np.floor(np.log10(R))

    # find resistor's index in valid_res
    i = valid_res.index(float(str(float(round(R,3))).replace('.','')[0:3])/10)

    while i + n >= len_valid_res: # allows overflow wrapping
        OOM += 1
        n -= len_valid_res
    while i + n <= -len_valid_res: # allows underflow wrapping 
        OOM -= 1
        n += len_valid_res

    # calculates the new resistor 
    return_val = valid_res[i + n]*10**(OOM-1)

    if return_val < 10: # bounds on allowed resistor values
        return 10
    elif return_val > 22*10**6:
        return 21.5*10**6
    else:
        return return_val

# runs a simulated annealing walk 
def run_walk(T : float, kMax : int, s_0 : dict, pbar=0):
    s = s_0.copy()
    sbest = s.copy()
    e = -CircuitAnalyzer(s).goodness
    ebest = e
    if T != 0: # accounts for zero temp (greedy random)
        b = T**(-2/kMax)
    else:
        b = 0

    for i in range(kMax):
        # annealing schedule
        T = temperature(T, b=b)
        # generates a nearby state
        snew = neighbour(s=s, free_vars=free_vars, sd=single.sigma)
        try: # simulates the circuit and calculates goodness
            enew = -CircuitAnalyzer(snew).goodness 
        except: # catches errors in NgSpice
            print(f"Something went wrong with: {snew}")
            enew = 0
        
        if P(e, enew, T): # acceptance 
            s = snew.copy()
            e = enew

        if enew < ebest: # records best
            sbest = snew.copy()
            ebest = enew

        if single.isVerbose and i%100 == 0: # verbose printing
            print(f"{round(i/kMax*100)}% Complete")
            print(f"Current Energy: {e:.2E}")
            print(f"    New Energy: {enew:.2E}")
            print()

        if not single.isVerbose: # non verbose output
            pbar.update()

    return sbest, ebest