import matplotlib.pyplot as plt
import numpy as np
import math

from PySpice.Probe.Plot import plot

# making bode plots
def bode_diagram(axes, frequency, gain, phase, **kwargs):
    bode_diagram_gain(axes[0], frequency, gain, **kwargs)
    bode_diagram_phase(axes[1], frequency, phase, **kwargs)

def bode_diagram_gain(axe, frequency, gain, **kwargs):
    axe.semilogx(frequency, gain, **kwargs)
    axe.grid(True)
    axe.grid(True, which='minor')
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("Gain [dB]")

def bode_diagram_phase(axe, frequency, phase, **kwargs):
    axe.semilogx(frequency, phase, **kwargs)
    axe.set_ylim(-math.pi, math.pi)
    axe.grid(True)
    axe.grid(True, which='minor')
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("Phase [rads]")
    # axe.set_yticks # Fixme:
    plt.yticks((-math.pi, -math.pi/2,0, math.pi/2, math.pi),
                  (r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"))

def make_bode_plot(analysis):
    figure, (ax1, ax2) = plt.subplots(2, figsize=(20, 10))
    plt.title("Bode Diagram of an Operational Amplifier")
    bode_diagram(axes=(ax1, ax2),
                frequency=analysis.frequency,
                gain=20*np.log10(np.absolute([x.value for x in np.absolute(analysis.AC_out)])),
                phase=np.angle([x.value for x in np.absolute(analysis.AC_out)], deg=False),
                marker='.',
                color='blue',
                linestyle='-',
                )
    ax1.hlines([61.5,58.5],[0,0],[100*10**6,100*10**6])
    plt.tight_layout()
    plt.show()

colors = ["red","green","blue"]
label = ["Start", "SA", "GRW"]

def make_bode_plot_from_list(analysis_list):
    figure, (ax1, ax2) = plt.subplots(2, figsize=(20, 10))
    plt.title("Bode Diagram of an Operational Amplifier")
    for i, analysis in enumerate(analysis_list):
        bode_diagram(axes=(ax1, ax2),
                    frequency=analysis.frequency,
                    gain=20*np.log10([x.value for x in np.absolute(analysis.AC_out)]),
                    phase=np.angle([x.value for x in analysis.AC_out], deg=False),
                    marker='.',
                    color=colors[i],
                    label=label[i],
                    linestyle='--',
                    )
    ax1.hlines([61.5,58.5],[0,0],[100*10**6,100*10**6])
    ax1.legend()
    plt.tight_layout()
    plt.show()

def make_2d_plot(x, y):
    plt.plot(x,y, 'o')
    plt.show()