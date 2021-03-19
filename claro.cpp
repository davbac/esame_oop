#include "claro.h"

int main() {
    std::string path="data-shell/secondolotto_1/";
    std::fstream elenco=open(path+"files_read.txt", std::ios::in);
//    std::fstream elenco (path+"prova.txt", std::ios::in);
    std::fstream outfile (path+"lin_cpp.txt", std::ios::out);
    std::string fname;
    outfile<<"N, M, Chip, Offset, Channel, TRANS, Width\n";
    while(elenco>>fname) {
        ClaroFile claro_file= ClaroFile{fname, path};
        outfile<<claro_file.lin_reg();
    }
}
