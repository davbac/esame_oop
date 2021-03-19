#include<iostream>
#include<fstream>
#include<string>
#include<vector>

std::string find_info(std::string const& name);
template<typename T> void linreg(std::vector<T>&, std::vector<T>&, double&, double&);

int main() {
    std::string path="data-shell/secondolotto_1/";
//     std::fstream elenco=open(path+"files_read.txt", std::ios::in);
    std::fstream elenco (path+"prova.txt", std::ios::in);
    std::fstream outfile (path+"lin_cpp.txt", std::ios::out);
    std::string fname;
    outfile<<"N, M, Chip, Offset, Channel, TRANS, Width\n";
    while(elenco>>fname) {
        std::string prefix=find_info(fname);
        outfile<<prefix<<", ";
        fname.replace(fname.begin(), fname.begin()+2, path); //get full file path
        std::fstream infile (fname);
        std::string line;
        std::vector<int> x, y, xfit, yfit;
        bool start=false;
        while(getline(infile,line)) {
            if(start) {
                size_t p=0;
                x.push_back(std::stoi(line, &p));
                y.push_back(std::stoi(line.substr(p), &p));
                
            }
            if(line.front()==' ' || line.front()=='\n' || line.front()=='\r') { // empty line
                start=true;
            }
        }
        int ind;
        for(int i=0; i<x.size(); i++) {
            if(y[i]>0 && y[i]<1000) {
                xfit.push_back(x[i]);
                yfit.push_back(y[i]);
                ind=i;
            }
        }
        if(xfit.size()==1) {
            xfit.push_back(x[ind-1]);
            xfit.push_back(x[ind+1]);
            yfit.push_back(y[ind-1]);
            yfit.push_back(y[ind+1]);
        } else if(xfit.size()==0) {
            xfit.push_back(x[0]);
            yfit.push_back(y[0]);
            for(int i=0; i<x.size(); i++) {
                if(y[i]<=0){
                    xfit[0]=x[i];
                    yfit[0]=y[i];
                } else {
                    xfit.push_back(x[i]);
                    yfit.push_back(y[i]);
                    break;
                }
            }
        }
        
        double a=0, b=0;
        linreg(xfit, yfit, a, b);
        
//         std::cout<<a<<" "<<b<<"  "<<(500-a)/b<<"\n";
        outfile<<(500-a)/b<<", "<<1000/b<<"\n";
    } 
//     std::cout<<"\n";
} 



std::string find_info(std::string const& name) { // get info (N, M, Chip, Channel, Offset) 
    size_t last_pos=0, pos;
    std::string res;
    std::vector<std::string> nums;
    do {
        pos=name.find_first_of("0123456789", last_pos+1);
        if(pos-last_pos>1) {
            nums.push_back(" "); //got errors otherwise
        }
        nums.back()+=name[pos];
        
        last_pos=pos;
    } while(pos!=name.npos);
    
    for(auto& s:nums) {
        s.erase(0,1);  //erase that leading space
    }
    res=nums[0]+", "+nums[1]+", "+nums[10]+", "+nums[12]+", "+nums[11];
    return res;
}

template <typename T> void linreg(std::vector<T>& x, std::vector<T>& y, double& a, double& b) {
    auto n=x.size();
    auto xm=0., ym=0., xy=0., x2=0.;
    for(int i=0; i<n; i++) {
        xm+=x[i];
        ym+=y[i];
        xy+=x[i]*y[i];
        x2+=x[i]*x[i];
    }
    xm/=n;
    ym/=n;
    
    b=(xy-n*xm*ym)/(x2-n*xm*xm);
    a=ym-b*xm;
}


