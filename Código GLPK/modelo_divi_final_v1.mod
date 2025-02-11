# Conjuntos
set K; # Níveis de cuidado
set P; # Tipos de pacientes
set I := {i in 1..524}; #Pontos de demanda
set E{K}; # Equipes de saúde por nível de cuidado
set EL{K}; # Unidades existentes por nível de cuidado
set L {k in K} := EL[k];

# Parâmetros
param C1{P, L[1]};    
param C2{L[2]}; 
param C3{L[3]}; 

param CE1{c1 in E[1]};   
param CE2{c2 in E[2]};
param CE3{c3 in E[3]};

param FC1{L[1]};   
param FC2{L[2]}; 
param FC3{L[3]}; 

param VC1{P, L[1]};   
param VC2{L[2]};
param VC3{L[3]};

param W{I, P};  

param MS1{E[1]};   
param MS2{E[2]};
param MS3{E[3]};

param CNES1{E[1], L[1]}; 
param CNES2{E[2], L[2]};
param CNES3{E[3], L[3]};

param U{K}; 

param O1{L[1]};    
param O2{L[2]};   

param D1{I,L[1]};
param D_10km{I,L[1]},binary;
param D2{L[1], L[2]};
param D3{L[2], L[3]};

param TC1{I,L[1]};
param TC2{L[1],L[2]};
param TC3{L[2],L[3]};



# Variáveis de decisão
var y{i in I, j1 in L[1]}, binary;
var y1{j1 in L[1]}, binary;
var y2{j2 in L[2]}, binary;
var y3{j3 in L[3]}, binary;

var u1{P, i in I, j1 in L[1]}, >=0;
var u2 {j1 in L[1], j2 in L[2]} >=0;
var u3 {j2 in L[2], j3 in L[3]}, >=0;

var l1{E[1], L[1]};
var l2{E[2], L[2]};
var l3{E[3], L[3]};

# Variável auxiliar: indica se há PHC disponível a =10 km
var delta{i in I}, binary;


minimize Custo:
    #Transporte
      sum{p in P, i in I, j1 in L[1]}D1[i,j1]*TC1[i,j1]*u1[p,i,j1] + sum{j1 in L[1], j2 in L[2]}D2[j1,j2]*TC2[j1,j2]*u2[j1,j2] + sum{j2 in L[2], j3 in L[3]}D3[j2,j3]*TC3[j2,j3]*u3[j2,j3]

    # Custo fixo em locais existentes
    + sum{j1 in EL[1]}FC1[j1]*y1[j1] + sum{j2 in EL[2]}FC2[j2]*y2[j2] + sum{j3 in EL[3]}FC3[j3]*y3[j3]


    # Custo variável por paciente
    + sum{p in P, i in I, j1 in L[1]} VC1[p,j1] * u1[p,i,j1]
    + sum{j1 in L[1], j2 in L[2]} VC2[j2] * u2[j1,j2]
    + sum{j2 in L[2], j3 in L[3]} VC3[j3] * u3[j2,j3];

 

# Fixa a variável - existe a localidade
s.t. Fixa1{j1 in EL[1]}: y1[j1] = 1;
s.t. Fixa2{j2 in EL[2]}: y2[j2] = 1;
s.t. Fixa3{j3 in EL[3]}: y3[j3] = 1;

# Cada ponto de demanda para cada local candidato
s.t. AtendeDemanda{i in I, j1 in L[1]}: sum{p in P}W[i,p]*y[i,j1] = sum{p in P}u1[p,i,j1];
s.t. AtendeDemanda1 {i in I}: sum{j1 in L[1]}y[i,j1] = 1;

# A população pode ser encaminhada para os níveis de atendimento
s.t. Encaminhamento{j1 in L[1]}: sum{j2 in L[2]}u2[j1,j2] = O1[j1] * sum{p in P, i in I}u1[p,i,j1];
s.t. Encaminhamento1{j2 in L[2]}: sum{j3 in L[3]}u3[j2,j3] = O2[j2] * sum{j1 in L[1]} u2[j1,j2];

# Equipe existente
s.t. EquipeExistente1{j1 in EL[1], e1 in E[1]}: sum{p in P, i in I}u1[p,i, j1]*MS1[e1] - l1[e1,j1] <= CNES1[e1,j1];
s.t. EquipeExistente2{j2 in EL[2], e2 in E[2]}: sum{j1 in L[1]}u2[j1,j2] * MS2[e2] - l2[e2,j2] <= CNES2[e2,j2];
s.t. EquipeExistente3{j3 in EL[3], e3 in E[3]}: sum{j2 in L[2]}u3[j2,j3] * MS3[e3] - l3[e3,j3] <= CNES3[e3,j3];


# Capacidade
s.t. Capacidade1{j1 in EL[1], p in P}: sum{i in I}u1[p,i,j1] <= C1[p,j1];
s.t. Capacidade2{j2 in EL[2]}: sum{j1 in L[1]}u2[j1,j2] <= C2[j2];
s.t. Capacidade3{j3 in EL[3]}: sum{j2 in L[2]}u3[j2,j3] <= C3[j3];


solve;





printf "\n===================================================\n";
printf "Planejamento Divinopolis\n";
printf "===================================================\n\n";

printf "Custo Logístico:\t$%.2f\n",
     sum{p in P, i in I, j1 in L[1]}D1[i,j1]*TC1[i,j1]*u1[p,i,j1]
    + sum{j1 in L[1], j2 in L[2]}D2[j1,j2]*TC2[j1,j2]*u2[j1,j2]
    + sum{j2 in L[2], j3 in L[3]}D3[j2,j3]*TC3[j2,j3]*u3[j2,j3];

printf "Custo Fixo PHC [E] :\t$%.2f\n",
    sum{j1 in EL[1]}FC1[j1]*y1[j1];
printf "Custo Fixo SHC [E]:\t$%.2f\n",
    + sum{j2 in EL[2]}FC2[j2]*y2[j2];
printf "Custo Fixo THC [E]:\t$%.2f\n",    
    + sum{j3 in EL[3]}FC3[j3]*y3[j3];
    
printf "Custo Variável PHC:\t$%.2f\n",
    sum{p in P, i in I, j1 in L[1]}VC1[p,j1]*u1[p,i,j1];
printf "Custo Variável SHC:\t$%.2f\n",
    sum{j1 in L[1], j2 in L[2]} VC2[j2] * u2[j1,j2];
printf "Custo Variável THC:\t$%.2f\n",
    sum{j2 in L[2], j3 in L[3]} VC3[j3] * u3[j2,j3];
printf "Custo Total:\t\t$%6.2f\n", Custo;
printf "\n__________________________________________________\n";

printf "\n===================================================\n";
printf "Pontos de Demanda       Pop.    Fluxo\n";
printf "===================================================\n";

for { i in I } {
    printf "\t[%2d]              %1.0f    %1.0f\n",
      i,
      ( sum{ p in P } W[i,p] ),               
      ( sum{ p in P, j1 in L[1] } u1[p,i,j1] );   
}

printf "___________________________________________________\n";
printf "Pontos de Demanda   ->  PHC    Fluxo\n";
printf "___________________________________________________\n";

for{i in I}{
    printf "\tM[%2d]          %1.0f    %1.0f\n", i, sum{p in P}W[i,p];
    for {j1 in L[1]: sum{p in P}u1[p,i,j1] > 0}{
        printf "\t>  L[%-1d]: %d\n", j1, sum{p in P}u1[p,i,j1];
    }
}

printf "___________________________________________________\n";
printf "PHC       > SHC   :Fluxo\n";
printf "___________________________________________________\n";

for{j1 in L[1]: sum{p in P,i in I}u1[p,i,j1] > 0}{
    printf "L[%-1d] > \t: %d\n", j1, O1[j1]*sum{p in P,i in I}u1[p,i,j1];
    for{j2 in L[2]: u2[j1,j2] > 0}{
        printf "\t> L[%-3d]: %d\n", j2, u2[j1,j2];
        
        
        

    }
}

printf "___________________________________________________\n";
printf "SHC    > THC   :(flow)\n";
printf "___________________________________________________\n";

for{j2 in L[2]: sum{j1 in L[1]}u2[j1,j2] > 0}{
    printf "L[%-1d] > \t: %d\n", j2, O2[j2]*sum{j1 in L[1]}u2[j1,j2];
    for{j3 in L[3]: u3[j2,j3] > 0}{
        printf "\t> L[%-4d]: %d\n", j3, u3[j2,j3];
    }
}

printf "\n===================================================\n";
printf "Equipes de Saúde\n";
printf "===================================================\n\n";
printf "___________________________________________________\n";
printf "PHC-Equipes\tQuantidade\tFalta/Excesso\n";
printf "___________________________________________________\n";

for{j1 in EL[1]: sum{p in P,i in I}u1[p,i,j1] > 0}{
    printf "L[%-2d]\n", j1;
    for{e1 in E[1]}{
        printf "[%-s]: %.2f\t\t%.2f\t\t%.2f\n", e1, CNES1[e1,j1],
        sum{p in P, i in I}u1[p,i,j1]*MS1[e1],
        l1[e1,j1];
    }
}


printf "\n\n___________________________________________________\n";
printf "SHC-Equipes\tQuantidade\tFalta/Excesso\n";
printf "___________________________________________________\n";
for{j2 in EL[2]: sum{j1 in L[1]}u2[j1,j2] > 0}{
    printf "L[%-2d]\n", j2;
    for{e2 in E[2]}{
        printf "[%--s]: %.2f\t\t%.2f\t\t%.2f\n", e2, CNES2[e2,j2],
        sum{j1 in L[1]}u2[j1,j2]*MS2[e2],
        l2[e2,j2];
    }
}


printf "\n\n___________________________________________________\n";
printf "THC-Equipes CNES\tQuantidade\tFalta/Excesso\n";
printf "___________________________________________________\n";
for{j3 in EL[3]: sum{j2 in L[2]}u3[j2,j3] >0}{
    printf"L[%-2d]\n",j3;
    for {e3 in E[3]}{
    printf "[%-s] %2.f\t%.2f\t%.2f\n", e3, CNES3[e3,j3],
    sum{j2 in L[2]}u3[j2,j3]*MS3[e3],
    l3[e3,j3];
    }
}


printf "\n\n====================================================\n";
printf "PHC [p]:    Capacidade Fluxo   Uso(%%)\n";
printf "====================================================\n";
printf{j1 in EL[1], p in P}:
"[%-3d][%d]:\t%d\t%d\t%3d%%\n", j1, p,
C1[p,j1],
sum{i in I}u1[p,i,j1],
((sum{i in I}u1[p,i,j1])/(C1[p,j1]))*100;


printf "\n\n====================================================\n";
printf "SHC [p]:    Capacidade Fluxo   Uso(%%)\n";
printf "====================================================\n";
printf{j2 in EL[2]} "[%-6d]\t%d\t%d\t%3d%%\n", j2,
C2[j2],
sum{j1 in L[1]}u2[j1,j2],
((sum{j1 in L[1]}u2[j1,j2])/(C2[j2]))*100;


printf "\n\n====================================================\n";
printf "THC [p]:    Capacidade Fluxo   Uso(%%)\n";
printf "====================================================\n";
printf{j3 in EL[3]} "[%-6d]\t%d\t%d\t%3d%%\n", j3,
C3[j3],
sum{j2 in L[2]}u3[j2,j3],
((sum{j2 in L[2]}u3[j2,j3])/(C3[j3]))*100;
printf "\n\n====================================================\n";



printf "\n======================================================================\n";
printf "Pontos de Demanda com fluxo para PHC e distância > 10 km\n";
printf "=========================================================================\n";

for {i in I: sum{j1 in L[1]} D_10km[i,j1] * sum{p in P} u1[p,i,j1] > 0} {
    printf "\tM[%2d]          %1.0f    %1.0f\n", i, sum{p in P} W[i,p];
    for {j1 in L[1]: D_10km[i,j1] == 1 && sum{p in P} u1[p,i,j1] > 0} {
        printf "\t>  L[%-1d]: %d (Distância: %.2f km)\n", j1, sum{p in P} u1[p,i,j1], D1[i,j1];
    }
}

printf "________________________________________________________________________\n";

# Imprimindo os valores de u1 em formato CSV
printf "PontoDemanda,PHC,Fluxo\n" > "fluxo_pd_phc_glpk.csv";
printf{i in I, p in P,j1 in L[1]: u1[p,i,j1] > 0} "%d,%d,%.2f\n", i, j1, u1[p,i,j1] >> "fluxo_pd_phc_glpk.csv";

# Criando o cabeçalho do arquivo CSV
printf "PHC,SHC,Fluxo\n" > "fluxo_phc_shc_glpk.csv";
printf{j1 in L[1], j2 in L[2]: u2[j1, j2] > 0} "%d,%d,%.2f\n", j1, j2, u2[j1, j2] >> "fluxo_phc_shc_glpk.csv";

# Criando o cabeçalho do arquivo CSV para SHC -> THC
printf "SHC,THC,Fluxo\n" > "fluxo_shc_thc_glpk.csv";
printf{j2 in L[2], j3 in L[3]: u3[j2, j3] > 0} "%d,%d,%.2f\n", j2, j3, u3[j2, j3] >> "fluxo_shc_thc_glpk.csv";

end;
