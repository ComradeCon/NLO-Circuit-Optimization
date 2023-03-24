import matplotlib.pyplot as plt
import numpy as np

from PySpice.Plot.BodeDiagram import bode_diagram
from PySpice.Probe.Plot import plot

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
    plt.tight_layout()
    plt.show()

colors = ["red","green"]

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
                    linestyle='--',
                    )
    plt.tight_layout()
    plt.show()

def make_2d_plot(x, y):
    plt.plot(x,y, 'o')
    plt.show()
