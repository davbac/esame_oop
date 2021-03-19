
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import erf
import re

def erf_param(x, a, f, w):
    return a*(erf(x*w-f)+1)/2


#elenco=open("data-shell/secondolotto_1/files_read.txt", "r")
elenco=open("data-shell/secondolotto_1/prova.txt", "r")
lin_file=open("data-shell/secondolotto_1/lin_py.txt", "w")
erf_file=open("data-shell/secondolotto_1/erf_py.txt", "w")
errlog=open("errlog.txt", "w")

lin_file.write("N, M, Chip, Offset, Channel, TRANS, Width\n")
erf_file.write("N, M, Chip, Offset, Channel, TRANS, Width\n")
first=True
for line in elenco:
    fn=line.strip().replace(".", "data-shell/secondolotto_1",1)
    if(fn==""):
        continue
    
    #get N, M, chip, offset, channel
    id_data=re.split("[^0-9]", line)
    id_data=[s for s in id_data if s!=""]
    id_str=str(id_data[0])+", "+str(id_data[1])+", "+str(id_data[10])+", "+str(id_data[12])+", "+str(id_data[11])+", "
    
    f=open(fn, "r")
    x=[]
    y=[]
    start=False
    for s in f:
        if(start):
            l=s.split()
            x.append(int(l[0]))
            y.append(int(l[1]))
        
        if(s.startswith(" ") or s=="\n"):
            start=True
    
    #linear fit
    xfit=[]
    yfit=[]
    ind=None
    for i in range(len(x)):
        if(0<y[i]<1000):
            xfit.append(x[i])
            yfit.append(y[i])
            ind=i
    if(len(xfit)==1):
        xfit.append(x[ind-1])
        yfit.append(y[ind-1])
        xfit.append(x[ind+1])
        yfit.append(y[ind+1])
    elif(len(xfit)==0):
        xfit.append(x[0])
        yfit.append(y[0])
        for i in range(len(x)):
            if(y[i]<=0):
                xfit[0]=x[i]
                yfit[0]=y[i]
            else:
                xfit.append(x[i])
                yfit.append(y[i])
                break
    
            
    
    a, b = np.polyfit(xfit, yfit, 1)
    lin_res=(500-b)/a
    #print("linear fit: ", lin_res)
    ygen=[X*a+b for X in xfit]
    plt.plot(x,y)
    plt.plot(xfit, ygen)
    lin_file.write(id_str+str(lin_res)+", "+str(1000/a)+"\n")
    
    try:
        #erf fit 
        popt, pcov=curve_fit(erf_param, x, y, p0=[1000, lin_res, 1])
        #print("erf fit: ", popt[1])
        x_erf_fit=np.linspace(x[0], x[-1], 100)
        y_erf_fit=[erf_param(X, *popt) for X in x_erf_fit]
        plt.plot(x_erf_fit, y_erf_fit)
        erf_file.write(id_str+str(popt[1])+", "+str(popt[2])+"\n")
    except RuntimeError:
        print("could't find erf parameters for "+fn)
        errlog.write(fn+"\n")
    
    #plt.show()
    if(first):
        plt.savefig("example.png");
        first=False
    
    
    
erf_file.close()
lin_file.close()
elenco.close()
errlog.close()
