import numpy as np
from PySpice.Unit import *
from circuit_analysis import *
from tqdm import tqdm
from helper_funcs import single

def temperature(T, b=0.833):
    return T*b

def P(E_past, E_new, T):
    if(E_new >= -1):
        return False
    temp = E_new - E_past
    if temp < 0:
        return True
    temp /= T*abs(E_past)/2
    if temp < 4:
        return 1/(1 + np.exp(temp)) > np.random.random()
    else:
        return False
    
# define free variables 
free_vars = ['RF','cascode1','cascode2','outStage']
free_vars_dict = {
    'cascode1' : ['RB1','RB2','RB3','RC','RE_deg','RE'],
    'cascode2' : ['RB1','RB2','RB3','RC','RE_deg','RE'],
    'outStage' : ['RE']
}

def neighbour(s, free_vars, sd=2):
    s_new = s.copy()
    for key in free_vars:
        if type(s[key]) == dict:
            s_new[key] = neighbour(s[key], free_vars=free_vars_dict[key], sd=sd)
        else:
            s_new[key] = iter_resistor(s[key], round(np.random.normal(0,sd)))
    return s_new

valid_res = [10.0, 10.5, 11.0, 11.5, 12.1, 12.7, 13.3, 14.0, 14.7, 15.4, 16.2, 16.9, 17.8, 18.7,
             19.6, 20.5, 21.5, 22.6, 23.7, 24.9, 26.1, 27.4, 28.7, 30.1, 31.6, 33.2, 34.8, 36.5, 
             38.3, 40.2, 42.2, 44.2, 46.4, 48.7, 51.1, 53.6, 56.2, 59.0, 61.9, 64.9, 68.1, 71.5, 
             75.0, 78.7, 82.5, 86.6, 90.9, 95.3]
len_valid_res = len(valid_res)

def iter_resistor(R,n):
    if n == 0:
        return R

    OOM = np.floor(np.log10(R))
    i = valid_res.index(float(str(float(round(R,3))).replace('.','')[0:3])/10)

    while i + n >= len_valid_res:
        OOM += 1
        n -= len_valid_res
    while i + n <= -len_valid_res:
        OOM -= 1
        n += len_valid_res
    return_val = valid_res[i + n]*10**(OOM-1)

    if return_val < 10:
        return 10
    elif return_val > 22*10**6:
        return 21.5*10**6
    else:
        return return_val
      
def final_run_walk(s_0: dict, k : int):
    e_0 = -CircuitAnalyzer(s_0).goodness
    ebest = e_0
    sbest = s_0.copy()
    if not single.isVerbose:
        for i in tqdm(range(int(k))):
            snew = neighbour(s=sbest, free_vars=free_vars, sd=single.sigma)
            try:
                enew = -CircuitAnalyzer(snew).goodness
            except:
                print(f"Something went wrong with: {snew}")
                enew = 0

            if enew < ebest:
                sbest = snew.copy()
                ebest = enew
    else:
        for i in range(int(k)):
            snew = neighbour(s=sbest, free_vars=free_vars, sd=single.sigma)
            try:
                enew = -CircuitAnalyzer(snew).goodness
            except:
                print(f"Something went wrong with: {snew}")
                enew = 0

            if enew < ebest:
                sbest = snew.copy()
                ebest = enew

            if single.isVerbose and i%100 == 0:
                print(f"{round(i/k*100)}% Complete")
                print(f"Best Energy: {ebest:.2E}")
                print(f" New Energy: {enew:.2E}")
                print()
    print(f"Improvement: {abs(ebest-e_0):0.2E}")
    return sbest, ebest

def run_walk(T : float, kMax : int, s_0 : dict, pbar=0):
    Tmax = T
    s = s_0.copy()
    sbest = s.copy()
    e = -CircuitAnalyzer(s).goodness
    ebest = e
    eplison = 10**(-5)
    b = (eplison/T)**(1/kMax)

    for i in range(kMax):
        T = temperature(T, b=b)
        snew = neighbour(s=s, free_vars=free_vars, sd=single.sigma)
        try:
            enew = -CircuitAnalyzer(snew).goodness
        except:
            print(f"Something went wrong with: {snew}")
            enew = 0
        
        if P(e, enew, T):
            s = snew.copy()
            e = enew

        if enew < ebest:
            sbest = snew.copy()
            ebest = enew

        if single.isVerbose and i%100 == 0:
            print(f"{round(i/kMax*100)}% Complete")
            print(f"Current Energy: {e:.2E}")
            print(f"    New Energy: {enew:.2E}")
            print()

        if not single.isVerbose:
            pbar.update()

    return sbest, ebest