from sipm_wf_class import *
#import sys

files=(("r20dcr3ov.csv", "r203ovwav.csv"), ("r204ov.csv", "r204ovwav.csv"), ("r205ov.csv", "r205ovwav.csv"))
#files=(("R00020_20ThermalCycles_OV3/Timestamp.csv", "R00020_20ThermalCycles_OV3/Waveform.csv"),)

n_pts_bsl=500
pk_hei=0.001
pk_prom=0.0001

for i in files:
    print(i)
    _sipm_wf_=sipm_wf(*i)
    _sipm_wf_.analyze_wf(n_pts_bsl, pk_hei, pk_prom, i[1].replace(".csv", ""))
    fig, ax=plt.subplots(2,1, sharex=True, gridspec_kw={"height_ratios":[2,1]})
    _sipm_wf_.show(ax, fig, i[1].replace(".csv", ""))
    _sipm_wf_.calc_dcr()
