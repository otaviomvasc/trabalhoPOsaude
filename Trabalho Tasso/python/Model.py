from pulp import LpProblem, LpMinimize, lpSum, LpVariable, GUROBI_CMD,LpBinary
import time
from Data import Data, Data_test
import json

def make_var_name(prefix, *args, max_len=10):
    # Truncate each argument to max_len characters to keep names short
    truncated = [str(arg)[:max_len] for arg in args]
    return prefix + "_" + "_".join(truncated)

class Hierarchical:
    def __init__(self, data: dict):
        self.set_data(data)

    def set_data(self, data):
        self.I = data['I']# pontos de demanda ok
        self.K = data['K']# sem uso
        self.P = data['P']# com ou sem doencças cronicas
        self.E  = data['E']# time  equipe de saude por nivel
        self.EL = data['EL']# unidades de saudes existentes nivel 1 2 3
        self.W = data['W']# tamanho de demanda

        self.CL = data['CL']# unidades candidatas no nivel 1 2 3 
        self.L  = data['L']# total El+Cl
        ########################
        self.CE = data['CE']# custo de equipe 

        self.D  = data['D']# matriz de distancia
        
        self.TC = data['TC']# custo de travessia 
        self.VC = data['VC']
        
        self.FC = data['FC']
        
        self.MS = data['MS']
        
        self.CNES = data['CNES']
        
        self.C = data['C']
        self.U = data['U']

        self.O = data['O']

    def Model(self):
        I, K, P, E, EL, CL, L = self.I, self.K, self.P, self.E, self.EL, self.CL, self.L
        
        VC = self.VC
        CE= self.CE
        D= self.D
        TC= self.TC
        FC = self.FC
        W, MS= self.W, self.MS
        CNES = self.CNES
        C = self.C
        U, O= self.U, self.O

        # Create numeric mappings for each domain.
        p_   = {p: str(n) for n, p in enumerate(P, start=1)}
        l_   = {k: {j: str(n) for n, j in enumerate(L[k], start=1)} for k in range(0, len(K) + 1)}
        e_   = {k: {e: str(n) for n, e in enumerate(E[k], start=1)} for k in K}


        model = LpProblem("Hierarchical", LpMinimize)
        
        y ={k: {j: LpVariable(name =f"y{str(k)}_{l_[k][j]}", cat=LpBinary) for j in L[k]} for k in K}
        u ={k: {(p, j1, j2): LpVariable(name =f"u{str(k)}_{p_[p]}_{l_[k-1][j1]}_{l_[k][j2]}", lowBound=0) for p in P for j1 in L[k-1] for j2 in L[k]} for k in K}
        l ={k: {(e, l): LpVariable(name =f"l{str(k)}_{e_[k][e]}_{l_[k][l]}") for e in E[k] for l in L[k]} for k in K}


        print("Objective function")
        start = time.time()
        custo_deslocamento =  sum(lpSum(D[k][j1][j2] * TC[k][j1][j2] * u[k][p, j1, j2] for p in P for j1 in L[k-1] for j2 in L[k]) for k in K)
        custo_equipe = sum(lpSum(CE[k][e] * y[k][j ] for j  in CL[k] for e in E[k]) for k in K)
        custo_fixo = sum(lpSum(FC[k][j] * y[k][j] for j in EL[k]) for k in K)
        custo_atendimento = sum(lpSum(VC[k][p, j2] * u[k][p, j1, j2] for p in P for j1 in L[k-1] for j2 in L[k]) for k in K)
        
        model.objective =   custo_deslocamento + custo_fixo + custo_equipe + custo_atendimento
        print("Total time: "  + str(time.time() - start))


        print("Fix the location variables of existing health care units")
        start = time.time()
        for k in K:
            for j in EL[k]: 
                model += y[k][j] == 1
        print("Total time: "  + str(time.time() - start))
        
        
        print("Universal coverage")
        start = time.time()
        for i in L[0]:
            model += lpSum(u[1][p, i, j1] for p in P for j1 in L[1]) ==  sum(W[i, p] for p in P)
        for j1 in L[1]:
            model += lpSum(u[2][p, j1, j2]for p in P for j2 in L[2]) == O[1][j1] * lpSum(u[1][p, j, j1]for p in P for j in L[0])
        for j2 in L[2]:
            model += lpSum(u[3][p, j2, j3]for p in P for j3 in L[3]) == O[2][j2] * lpSum(u[2][p, j, j2]for p in P for j in L[1])
        print("Total time: "  + str(time.time() - start))
        
        
        print("Optimize existing location health care team")
        start = time.time()
        for k in K:
            for j in EL[k]:
                for e in E[k]:
                    model += lpSum(u[k][p, i, j] for p in P for i in EL[k-1])* MS[k][e] - l[k][e,j ] == CNES[k][j][e]
        print("Total time: "  + str(time.time() - start))
        
        
        print("Optimize new location health care team")
        start = time.time()
        for k in K:
            for j in CL[k]:
                for e in E[k]:
                    model += lpSum(u[k][p, i, j] for p in P for i in L[k-1])* MS[k][e] == l[k][e,j ]
        print("Total time: "  + str(time.time() - start))
        
        
        print("Existing health care units have limited capacity")
        start = time.time()
        for k in K:
            for j in EL[k]:
                model += lpSum(u[k][p, i, j] for i in L[k-1] for p in P) <= C[k][j]
        print("Total time: "  + str(time.time() - start))
        
        
        print("New health care units have limited capacity")
        start = time.time()
        for k in K:
            for j in CL[k]:
                model += lpSum(u[k][p, i, j] for i in L[k-1] for p in P) <=  C[k][j]* y[k][j]
        print("Total time: "  + str(time.time() - start))
        
        
        print("New health care units have limited capacity")
        start = time.time()
        for k in K:
            model += lpSum(y[k][j] for j in CL[k]) <= U[k]
        print("Total time: "  + str(time.time() - start))


        self._model = model
        self.y, self.u, self.l = y, u, l

    def run(self):
        print("Solving the model...")
        start_time = time.time()
        # self._model.solve()  # instantiate GUROBI_CMD
        self._model.solve(GUROBI_CMD())  # instantiate GUROBI_CMD
        end_time = time.time()
        self.solutionTime = end_time - start_time

    def print_solution(self):
        I, K, P, E, EL, CL, L = self.I, self.K, self.P, self.E, self.EL, self.CL, self.L
        # Use dictionary indexing for level-dependent parameters
        VC1, VC2, VC3 = self.VC[1], self.VC[2], self.VC[3]
        CE1, CE2, CE3 = self.CE[1], self.CE[2], self.CE[3]
        D1, D2, D3 = self.D[1], self.D[2], self.D[3]
        TC1, TC2, TC3 = self.TC[1], self.TC[2], self.TC[3]
        FC1, FC2, FC3 = self.FC[1], self.FC[2], self.FC[3]
        MS1, MS2, MS3 = self.MS[1], self.MS[2], self.MS[3]
        CNES1, CNES2, CNES3 = self.CNES[1], self.CNES[2], self.CNES[3]
        C1, C2, C3 = self.C[1], self.C[2], self.C[3]
        U = self.U  # expect U[1], U[2], U[3]
        # Access solution variables via dictionaries
        y = self.y     # y[1], y[2], y[3]
        u = self.u     # u[1], u[2], u[3]
        
        if self._model.status:
            logist_cost =  sum(D1[i][j] * TC1[i][j] * (u[1][(p, i, j)].value() or 0) for p in P for i in I for j in L[1]) + \
                           sum(D2[j][j2] * TC2[j][j2] * (u[2][(p, j, j2)].value() or 0) for p in P for j in L[1] for j2 in L[2]) + \
                           sum(D3[j2][j3] * TC3[j2][j3] * (u[3][(p, j2, j3)].value() or 0) for p in P for j2 in L[2] for j3 in L[3])
            fixed_cost_E = sum(FC1[j] for j in EL[1]) + sum(FC2[j] for j in EL[2]) + sum(FC3[j] for j in EL[3])
            fixed_cost_C = sum(FC1[j1] * (y[1][j1].value() or 0) for j1 in CL[1]) + \
                           sum(FC2[j2] * (y[2][j2].value() or 0) for j2 in CL[2]) + \
                           sum(FC3[j3] * (y[3][j3].value() or 0) for j3 in CL[3])
            new_team_cost_C = sum(CE1[e] * (y[1][j1].value() or 0) for j1 in CL[1] for e in E[1]) + \
                              sum(CE2[e] * (y[2][j2].value() or 0) for j2 in CL[2] for e in E[2]) + \
                              sum(CE3[e] * (y[3][j3].value() or 0) for j3 in CL[3] for e in E[3])
            variable_cost = sum(D1[i][j1] * TC1[i][j1] *
                                (u[1][(p, i, j1)].value() or 0) * VC1[p, j1]
                                for p in P for i in I for j1 in L[1]) + \
                            sum(D2[j1][j2] * TC2[j1][j2] *
                                (u[2][(p, j, j2)].value() or 0) * VC2[p, j2]
                                for p in P for j1 in L[1] for j2 in L[2]) + \
                            sum(D3[j2][j3] * TC3[j2][j3] *
                                (u[3][(p, j2, j3)].value() or 0) * VC3[p, j3]
                                for p in P for j2 in L[2] for j3 in L[3])
            total = logist_cost + fixed_cost_E + fixed_cost_C + new_team_cost_C + variable_cost
            print("==================================")
            print("Health Care Plan")
            print("==================================")
            print(f"Logist cost: ${logist_cost:.2f}")
            print(f"Fixed cost [E]: ${fixed_cost_E:.2f}")
            print(f"Fixed cost [C]: ${fixed_cost_C:.2f}")
            print(f"New team cost [C]: ${new_team_cost_C:.2f}")
            print(f"Variable Cost: ${variable_cost:.2f}")
            print(f"Hospital cost: ${total-logist_cost:.2f}")
            print("==================================")
            print(f"Total Cost: ${total:.2f}")
            print("==================================")
            print(f"demand: {sum(self.W[i, p] for i in I for p in P)}")
            print(f"demand: {sum(u[1][(p, i, j)].value() for p in P for i in I for j in L[1])}")

            print("New Units: Qty / Max Use(%)")
            print("==================================")
            phc_total = sum(y[1][j].value() or 0 for j in CL[1])
            shc_total = sum(y[2][j].value() or 0 for j in CL[2])
            thc_total = sum(y[3][j].value() or 0 for j in CL[3])
            print(f"PHC: {phc_total} -> {phc_total / U[1] * 100:.2f}%")
            print(f"SHC: {shc_total} -> {shc_total / U[2] * 100:.2f}%")
            print(f"THC: {thc_total} -> {thc_total / U[3] * 100:.2f}%")

            print("==================================")
            print("Municipality: Pop Flow")
            print("==================================")
            for i in L[0]:
                flow = sum(u[1][(p, i, j)].value() or 0 for p in P for j in L[1])
                print(f"[{i}]: {flow}")
            print("==================================")
            print("Mun > PHC :(flow)")
            print("==================================")
            for i in I:
                for j in L[1]:
                    flow = sum(u[1][(p, i, j)].value() or 0 for p in P)
                    if flow > 0:
                        print(f"M[{i} ] > : {flow}")
                        print(f"> L[{j} ]: {flow}")
            print("==================================")
            print("PHC > SHC :(flow)")
            print("==================================")
            for j in L[1]:
                for j2 in L[2]:
                    flow = sum(u[2][(p, j, j2)].value() or 0 for p in P)
                    if flow > 0:
                        print(f"L[{j} ] > : {flow}")
                        print(f"> L[{j2} ]: {flow}")
            print("==================================")
            print("SHC > THC :(flow)")
            print("==================================")
            for j2 in L[2]:
                for j3 in L[3]:
                    flow = sum(u[3][(p, j2, j3)].value() or 0 for p in P)
                    if flow > 0:
                        print(f"L[{j2} ] > : {flow}")
                        print(f"> L[{j3} ]: {flow}")
            print("==================================")
            print("Health care team (Existing and New*)")
            print("==================================")
            # print("==================================")
            # print("PHC-Team CNES Flow Lack/Excess")
            # print("==================================")
            # for j in EL[1]:
            #     print(f"L[{j} ]")
            #     for e in E[1]:
            #         flow = sum((u[1][(p, i, j)].value() or 0) * MS1[e] for p in P for i in I)
            #         cnes = CNES1[j][e]
            #         print(f"[{e}]: {cnes:.2f} {flow:.2f} {flow - cnes:.2f}")
            # print("==================================")
            # print("SHC-Team CNES Flow Lack/Excess")
            # print("==================================")
            # for j2 in EL[2]:
            #     print(f"L[{j2} ]")
            #     for e in E[2]:
            #         flow = sum((u[2][(p, j, j2)].value() or 0) * MS2[e] for p in P for j in L[1])
            #         cnes = CNES2[j2][e]
            #         print(f"[{e}]: {cnes:.2f} {flow:.2f} {flow - cnes:.2f}")
            # print("==================================")
            # print("THC-Team CNES Flow Lack/Excess")
            # print("==================================")
            # for j3 in EL[3]:
            #     print(f"L[{j3} ]")
            #     for e in E[3]:
            #         flow = sum((u[3][(p, j2, j3)].value() or 0) * MS3[e] for p in P for j2 in L[2])
            #         cnes = CNES3[j3][e]
            #         print(f"[{e}]: {cnes:.2f} {flow:.2f} {flow - cnes:.2f}")
            print("==================================")
            print("PHC [p]: Capty Met Use(%)")
            print("==================================")
            for j in L[1]:
                capty = C1[j]
                met = sum(u[1][(p, i, j)].value() or 0 for p in P for i in I )
                if met > 0.00001:
                    print(f"[{j}]: {capty} {met} {met / capty * 100:.2f}%")
            print("==================================")
            print("SHC : Capty Met Use(%)")
            print("==================================")
            for j2 in L[2]:
                capty = C2[j2]
                met = sum(u[2][(p, j, j2)].value() or 0 for p in P for j in L[1])
                if met > 0.00001:
                    print(f"[{j2}]: {capty} {met} {met / capty * 100:.2f}%")
            print("==================================")
            print("THC : Capty Met Use(%)")
            print("==================================")
            for j3 in L[3]:
                capty = C3[j3]
                met = sum(u[3][(p, j2, j3)].value() or 0 for p in P for j2 in L[2])
                if met > 0.00001:
                    print(f"[{j3}]: {capty} {met} {met / capty * 100:.2f}%")
            print("==================================")
        else:
            print("No optimal solution found.")

    def export_model(self, filename="model.lp"):
        self._model.writeLP(filename)

    def save_result(self, filename="flow_results.json"):
        I, K, P, E, EL, CL, L = self.I, self.K, self.P, self.E, self.EL, self.CL, self.L
        u = self.u
        flow_results = {}

        # Level 1: from L[0] to L[1]
        flow_results["1"] = {}
        for origin in L[0]:
            tmp = {}
            for dest in L[1]:
                total_flow = sum(u[1][(p, origin, dest)].value() or 0 for p in P)
                if total_flow > 0:
                    tmp[dest] = total_flow
            if tmp:
                flow_results["1"][origin] = tmp

        # Level 2: from L[1] to L[2]
        flow_results["2"] = {}
        for origin in L[1]:
            tmp = {}
            for dest in L[2]:
                total_flow = sum(u[2][(p, origin, dest)].value() or 0 for p in P)
                if total_flow > 0:
                    tmp[dest] = total_flow
            if tmp:
                flow_results["2"][origin] = tmp

        # Level 3: from L[2] to L[3]
        flow_results["3"] = {}
        for origin in L[2]:
            tmp = {}
            for dest in L[3]:
                total_flow = sum(u[3][(p, origin, dest)].value() or 0 for p in P)
                if total_flow > 0:
                    tmp[dest] = total_flow
            if tmp:
                flow_results["3"][origin] = tmp

        with open(filename, "w", encoding='utf-8') as f:
            json.dump(flow_results, f, indent=4,  ensure_ascii=False)

    def save_new_locations(self, filename="new_locations.json"):
        y = self.y
        new_locations = {}
        for k in self.K:
            new_locations[k] = [j for j in self.CL[k] if y[k][j].value()]
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(new_locations, f, indent=4,  ensure_ascii=False)

if __name__ == "__main__":
    # data = Data_test()
    data = Data()

    hierarchical_model = Hierarchical(data.get_data())
    hierarchical_model.Model()

    # Export the model to an LP file for debugging
    # hierarchical_model.export_model("debug_model.lp")

    # Validar modelo antes de resolver
    # if hierarchical_model.validate_model():
    hierarchical_model.run()
    hierarchical_model.save_result()
    hierarchical_model.save_new_locations()
    # else:
    #     print("O modelo contém erros e não pode ser resolvido.")
