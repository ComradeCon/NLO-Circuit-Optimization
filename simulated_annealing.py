import numpy as np
from PySpice.Unit import *
from circuit_analysis import *
from tqdm import tqdm

# s ← s0; e ← E(s)                                  // Initial state, energy.
# sbest ← s; ebest ← e                              // Initial "best" solution
# k ← 0                                             // Energy evaluation count.
# while k < kmax and e > emax                       // While time left & not good enough:
#   T ← temperature(k/kmax)                         // Temperature calculation.
#   snew ← neighbour(s)                             // Pick some neighbour.
#   enew ← E(snew)                                  // Compute its energy.
#   if P(e, enew, T) > random() then                // Should we move to it?
#     s ← snew; e ← enew                            // Yes, change state.
#   if enew < ebest then                            // Is this a new best?
#     sbest ← snew; ebest ← enew                    // Save 'new neighbour' to 'best found'.
#   k ← k + 1                                       // One more evaluation done
# return sbest             



def temperature(T, b=0.833):
    return T*b

k_B = 1000#1.38*10**(-23)

def P(E_past, E_new, T):
    temp = E_new - E_past
    if temp < 0:
        return True
    temp /= T
    if temp < 4:
        return 1/(1 + np.exp(temp)) > np.random.random()
    else:
        return False
 
        # num = np.exp(-E_new.value/(k_B*T))
        # denom = np.sum([np.exp(-E_i.value/(k_B*T)) for E_i in E_past])
        # return num/denom
        # return np.exp(-(E_new - E_past)/T)
    
# define free variables 
free_vars_full = ['RF','cascode1','cascode2', 'outStage']
free_vars_gain = ['cascode1', 'cascode2']
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
    
# s ← s0; e ← E(s)                                  // Initial state, energy.
# sbest ← s; ebest ← e                              // Initial "best" solution
# k ← 0                                             // Energy evaluation count.
# while k < kmax and e > emax                       // While time left & not good enough:
#   T ← temperature(k/kmax)                         // Temperature calculation.
#   snew ← neighbour(s)                             // Pick some neighbour.
#   enew ← E(snew)                                  // Compute its energy.
#   if P(e, enew, T) > random() then                // Should we move to it?
#     s ← snew; e ← enew                            // Yes, change state.
#   if enew < ebest then                            // Is this a new best?
#     sbest ← snew; ebest ← enew                    // Save 'new neighbour' to 'best found'.
#   k ← k + 1                                       // One more evaluation done
# return sbest         

def final_run_walk(s_0: dict, k : int, isFull):
    e_0 = -CircuitAnalyzer(s_0).goodness
    sbest = s_0.copy()
    ebest = e_0
    free_vars = None
    if isFull:
        free_vars = free_vars_full
    else:
        free_vars = free_vars_gain
    for i in tqdm(range(int(k))):
        snew = neighbour(s=sbest, free_vars=free_vars, sd=2)
        try:
            enew = -CircuitAnalyzer(snew,isFull).goodness
        except:
            print(f"Something went wrong with: {snew}")
            enew = 0

        if enew < ebest:
            sbest = snew.copy()
            ebest = enew
    print(f"Improvement: {abs(ebest-e_0):0.2E}")
    return sbest, ebest

def run_walk(T : float, kMax : int, s_0 : dict, pbar, isFull : bool):
    Tmax = T
    s = s_0.copy()
    sbest = s.copy()
    e = -CircuitAnalyzer(s,isFull).goodness
    ebest = e
    eplison = 10**(-5)
    b = (eplison/T)**(1/kMax)
    free_vars = None
    if isFull:
        free_vars = free_vars_full
    else:
        free_vars = free_vars_gain
    while T > eplison:
        T = temperature(T, b=b)
        snew = neighbour(s=s, free_vars=free_vars, sd=8*T/Tmax + 2)
        try:
            enew = -CircuitAnalyzer(snew,isFull).goodness
        except:
            print(f"Something went wrong with: {snew}")
            enew = 0

        # print(f'Rand:{np.random.random()}')
        # print(P(e, enew, e_0, T))
        
        if P(e, enew, T):
            s = snew.copy()
            e = enew

        if enew < ebest:
            sbest = snew.copy()
            ebest = enew

        pbar.update()

    return sbest, ebest