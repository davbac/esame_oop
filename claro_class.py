import matplotlib.pyplot as plt
import re
import numpy as np
from scipy.special import erf
from scipy.optimize import curve_fit



def erf_param(x, a, f, w):
    return a*(erf(x*w-f)+1)/2


class claro_file:
    def __init__(self, line, errlog):
        self.fn=line.strip().replace(".", "data-shell/secondolotto_1",1)
        self.errlog=errlog
        #get N, M, chip, offset, channel
        id_data=re.split("[^0-9]", line)
        id_data=[s for s in id_data if s!=""]
        self.id_str=str(id_data[0])+", "+str(id_data[1])+", "+str(id_data[10])+", "+str(id_data[12])+", "+str(id_data[11])+", "
    
        with open(self.fn, "r") as f:
            self.x=[]
            self.y=[]
            start=False
            for s in f:
                if(start):
                    l=s.split()
                    self.x.append(int(l[0]))
                    self.y.append(int(l[1]))
            
                if(s.startswith(" ") or s=="\n"):
                    start=True
    
    def lin_fit(self):
        self.xfit=[]
        self.yfit=[]
        ind=None
        for i in range(len(self.x)):
            if(0<self.y[i]<1000):
                self.xfit.append(self.x[i])
                self.yfit.append(self.y[i])
                ind=i
        if(len(self.xfit)==1):
            self.xfit.append(self.x[ind-1])
            self.yfit.append(self.y[ind-1])
            self.xfit.append(self.x[ind+1])
            self.yfit.append(self.y[ind+1])
        elif(len(self.xfit)==0):
            self.xfit.append(self.x[0])
            self.yfit.append(self.y[0])
            for i in range(len(self.x)):
                if(self.y[i]<=0):
                    self.xfit[0]=self.x[i]
                    self.yfit[0]=self.y[i]
                else:
                    self.xfit.append(self.x[i])
                    self.yfit.append(self.y[i])
                    break
        a, b = np.polyfit(self.xfit, self.yfit, 1)
        self.lin_res=(500-b)/a
        #print("linear fit: ", lin_res)
        self.ygen=[X*a+b for X in self.xfit]
        return self.id_str+str(self.lin_res)+", "+str(1000/a)+"\n"
        
    def erf_fit(self):
        #erf fit 
        popt, pcov=curve_fit(erf_param, self.x, self.y, p0=[1000, self.lin_res, 1])
        #print("erf fit: ", popt[1])
        self.x_erf_fit=np.linspace(self.x[0], self.x[-1], 100)
        self.y_erf_fit=[erf_param(X, *popt) for X in self.x_erf_fit]
        return self.id_str+str(popt[1])+", "+str(popt[2])+"\n"
        
    def plot(self):
        plt.plot(self.x,self.y)
        plt.plot(self.xfit, self.ygen)
        plt.plot(self.x_erf_fit, self.y_erf_fit)
        plt.show()


