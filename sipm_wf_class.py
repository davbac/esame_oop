import pandas as pd
import numpy as np
import scipy.signal as sp
import matplotlib.pyplot as plt
import progressbar


def read_table(fn, head):
    with open(fn) as f:
        lines=f.readlines()
    for i in range(len(lines)):
        if lines[i].startswith(head):
            return pd.read_csv(fn, header=i)
    print("no header found")
 
class sipm_wf:
    def __init__(self, tsf, wff):
        self.ts=read_table(tsf, "X: (s)")
        self.wf=read_table(wff, "TIME")
        self.ts.rename(columns={"X: (s)":"ev", "Y: (Hits)":"dt"}, inplace=True)
        self.ppwf=len(self.wf)//len(self.ts) #points per waveform
        self.totev=len(self.ts) #tot number of events
        self.ts["t"]=self.ts["dt"].cumsum()
        self.wf_peaks=pd.DataFrame()
    
    def analyze_wf_event(self, event,n_bsl, pk_hei=0.001, pk_prom=0.0001, folder_name="plot"):
        wf_ev_rg=[event*self.ppwf, (event+1)*self.ppwf] #range of indexes
        wf_time=self.wf["TIME"][wf_ev_rg[0]:wf_ev_rg[1]]+self.ts["t"].iloc[event] #time series
        """every event in the waveform file is saved with a deltatime referenced to a 0 placed in the 
        middle, the absolute time since the beginning of the experiment of this point is saved in
        the timestamp file"""
        wf_ch=-self.wf["CH1"].iloc[wf_ev_rg[0]:wf_ev_rg[1]] #would be negative, change sign for more human-readable peaks
        
        self.bsl=np.polyfit(wf_time[0:n_bsl], wf_ch[0:n_bsl], 0)[0] ##linear deg 0 fit, only first n_bsl elements
        bsl_time=wf_time[0:n_bsl] #time of the first points
        bsl_ch=[self.bsl]*n_bsl #just the baseline value repeated n_bsl times
        peaks,ndarray = sp.find_peaks(wf_ch,height=pk_hei,prominence=pk_prom)

        fig, ax = plt.subplots()
        plt.ticklabel_format(axis='x', style='sci', scilimits=(0,0))
        ax.plot(wf_time, wf_ch, linestyle='-', linewidth=1)
        ax.plot(bsl_time, bsl_ch, linestyle='-', linewidth=1, c='darkgreen')
        if len(peaks)>0: ax.scatter(wf_time.iloc[peaks], wf_ch.iloc[peaks],c='darkred')
        ax.set_ylabel('Amplitude (V)')
        ax.set_xlabel('Time (s)')
        plot_name = '{0}/ev{1}.png'.format(folder_name,event)
        fig.savefig(plot_name)
        plt.close(fig)
        # La funzione restituisce i valori di tempo e ampiezza (ottenuta come Ch1-baseline)..
        # ..agli indici dei massimi trovati da find_peaks
        return wf_time.iloc[peaks], wf_ch.iloc[peaks]-self.bsl
    
    def analyze_wf(self, n_bsl, pk_hei=0.001, pk_prom=0.0001, folder_name="plot"):
        print("analyzing wf")
        bar = progressbar.ProgressBar(maxval=self.totev, widgets=[progressbar.Bar("=", "[", "]"), " ", progressbar.Percentage()])
        bar.start()
        counter = 0 #to update bar
        for event in self.ts['ev']:
            peaks_time, peaks_ampl = self.analyze_wf_event(event, n_bsl, pk_hei, pk_prom, folder_name)
            #concatenate results to get overall
            self.wf_peaks = pd.concat([self.wf_peaks, pd.DataFrame({'t': peaks_time, 'A': peaks_ampl})], ignore_index=True)
            counter+=1
            bar.update(counter)
        bar.finish()
        
        self.wf_peaks['dt']=self.wf_peaks['t'].diff() #get dt prom absolute time
        self.wf_peaks=self.wf_peaks.iloc[1:] #leave out first value since it doesn't have a diff value
        print("Found "+str(len(self.wf_peaks))+" peaks\n")
        
    def show(self, ax, fig, folder_name="."):
        if(len(ax)!=2):
            raise ValueError("method needs 2 subplots to plot on")
        
        
        plt.xscale("log")
        
        figure_title = "Dark current plot"
        ax[0].set_title(figure_title)
        # Comincio con lo scatter plot di amplitude vs Dt in alto
        ax[0].scatter(self.wf_peaks['dt'],self.wf_peaks['A'],marker='o',facecolors='none',edgecolors='black')
        ax[0].set_xlim([1e-10,10])
        ax[0].set_ylim([0,0.01])
        ax[0].set_ylabel("Amplitudes (V)")
        # Poi creo il binning logaritmico per il plot di Dt..
        #log_bins = np.logspace(np.log10(bins[0]),np.log10(bins[-1]),len(bins))
        log_bins = np.logspace(np.log10(min(self.wf_peaks["dt"])),np.log10(max(self.wf_peaks["dt"])),100)
        # ..e il plot stesso
        ax[1].hist(self.wf_peaks['dt'],bins=log_bins,histtype='step')
        ax[1].set_yscale('log')
        ax[1].set_ylabel("counts")
        ax[1].set_xlabel(r"$\Delta$t (s)")
        
        plt.tight_layout()
        plt.subplots_adjust(hspace=0)

        fig.savefig(folder_name+"/Amplitude_vs_Dt.pdf")
        plt.close(fig)
        print("Plot saved as '"+folder_name+"/Amplitude_vs_Dt.pdf'\n")
        
    def calc_dcr(self):
        print("calculating dcr, ct & ap")
        # La dark count rate sara' uguale al numero di punti a Dt elevata..
        dcr = len(self.wf_peaks[ (self.wf_peaks['dt']> 4e-6) ])
        dcr_err = np.sqrt(dcr)
        # La rate dei cross-talk sara' uguale al numero di punti a ampiezza superiore a 1 pe..
        ctr = len(self.wf_peaks[ (self.wf_peaks['A']> 0.004) ])
        ctr_err = np.sqrt(ctr)
        # la rate dei after-pulse sara' uguale al numero di punti Dt piccolo..
        apr = len(self.wf_peaks[ (self.wf_peaks['dt']< 4e-6) & (self.wf_peaks['A']< 0.004) ] )
        apr_err = np.sqrt(apr)
        # ..divisi per la lunghezza del run..
        # ..che approssimativamente corrisponde al tempo dell'ultimo evento
        run_time = self.wf_peaks['t'].iloc[-1]
        dcr = dcr /run_time
        dcr_err = dcr_err/run_time
        ctr = ctr /run_time
        ctr_err = ctr_err/run_time
        apr = apr/run_time
        apr_err = apr_err/run_time
        # Stampo i valori su terminale
        print(r"Dark count rate = {:.2f} +/- {:.2f} s^(-1)".format(dcr,dcr_err))
        print(r"Cross-talk rate = {:.2f} +/- {:.2f} s^(-1)".format(ctr,ctr_err))
        print(r"After-pulse rate = {:.2f} +/- {:.2f} s^(-1)".format(apr,apr_err))
        print()




