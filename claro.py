from claro_class import *


elenco=open("data-shell/secondolotto_1/files_read.txt", "r")
#elenco=open("data-shell/secondolotto_1/prova.txt", "r")
lin_file=open("data-shell/secondolotto_1/lin_py.txt", "w")
erf_file=open("data-shell/secondolotto_1/erf_py.txt", "w")
errlog=open("errlog.txt", "w")

lin_file.write("N, M, Chip, Offset, Channel, TRANS, Width\n")
erf_file.write("N, M, Chip, Offset, Channel, TRANS, Width\n")


for line in elenco:
    if(line.strip()==""):
        continue
    _claro_file_=claro_file(line, errlog)
    lin_file.write(_claro_file_.lin_fit())
    try:
        erf_file.write(_claro_file_.erf_fit())
    except RuntimeError:
            print("could't find erf parameters for "+_claro_file_.fn)
            errlog.write(_claro_file_.fn+"\n")

erf_file.close()
lin_file.close()
errlog.close()
elenco.close()
