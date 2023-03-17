import numpy as np
from PySpice.Unit import *
from circuit_analysis import *

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

def P(E_past, E_new, E_0, T):
    if E_past > E_new:
        return 1
    else:
        # better for some reason 
        # num = np.exp(-E_new.value/(k_B*T))
        # denom = np.sum([np.exp(-E_i.value/(k_B*T)) for E_i in E_past])
        # return num/denom
        # return np.exp(-(E_new - E_past)/T)
        return 1/(1 + np.exp((E_new-E_past)/(T*E_0)))
    
def neighbour(s, free_vars, sd=2):
    s_new = s.copy()
    for key in free_vars:
        s_new[key] = iter_resistor(s[key], int(np.random.normal(0,sd)))
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
    i = valid_res.index(float(str(round(R,3)).replace('.','')[0:3])/10)
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

def run_walk(T : float, kMax : int, s_0 : dict, free_vars : list, pbar):
    s = s_0.copy()
    sbest = s.copy()
    e = -CircuitAnalyzer(s).goodness
    e_0 = e
    ebest = e
    eplison = 10**(-5)
    b = (eplison/T)**(1/kMax)

    while T > eplison:
        T = temperature(T, b=b)
        snew = neighbour(s=s, free_vars=free_vars, sd=10)
        try:
            enew = -CircuitAnalyzer(s).goodness
        except:
            print(f"Something went wrong with: {snew}")
            enew = 0

        if P(e, enew, e_0, T) > np.random.random():
            s = snew.copy()
            e = enew

        if enew < ebest:
            sbest = snew.copy()
            ebest = enew

        pbar.update()

    return sbest, ebest