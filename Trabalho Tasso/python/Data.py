import json

class Data:
    def __init__(self):
        self.demand_file = 'P.O Saude/dados_json/bairro_demanda_set.json'
        self.level_files = {
            1: 'P.O Saude/dados_json/EL_1.json',
            2: 'P.O Saude/dados_json/EL_2.json',
            3: 'P.O Saude/dados_json/EL_3.json'}
        self.equipe_files = {
            1: 'P.O Saude/dados_json/Equipe_1.json',
            2: 'P.O Saude/dados_json/Equipe_2.json',
            3: 'P.O Saude/dados_json/Equipe_3.json'}
        self.cnes_files = {
            1: 'P.O Saude/dados_json/CNES_1.json',
            2: 'P.O Saude/dados_json/CNES_2.json',
            3: 'P.O Saude/dados_json/CNES_3.json'}
        self.distance_files = {
            1: 'P.O Saude/dados_json/distance_matrix_1.json',
            2: 'P.O Saude/dados_json/distance_matrix_2.json',
            3: 'P.O Saude/dados_json/distance_matrix_3.json'}
        self.newLevel_files = {
            1: 'P.O Saude/dados_json/novas_unidades_nivel_1.json',
            2: 'P.O Saude/dados_json/novas_unidades_nivel_2.json',
            3: 'P.O Saude/dados_json/novas_unidades_nivel_3.json'}
        self.MS = 'P.O Saude/dados_json/MS.json'
        self.capacity = 'P.O Saude/dados_json/capacidade.json'
    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_data(self):
        demand_data = self.load_json(self.demand_file)
        level_data = {level: self.load_json(file) for level, file in self.level_files.items()}
        equipe_data = {level: self.load_json(file) for level, file in self.equipe_files.items()}
        cnes_data = {level: self.load_json(file) for level, file in self.cnes_files.items()}
        distance_data = {level: self.load_json(file) for level, file in self.distance_files.items()}
        newLevel_data = {level: self.load_json(file) for level, file in self.newLevel_files.items()}
        ms = self.load_json(self.MS)
        cap = self.load_json(self.capacity)
        I = [d['NOME'] for d in demand_data]
        K = [1, 2, 3]
        P = [1, 2]

        E = {level: list(equipe["descricao_cbo"]) for level, equipe in equipe_data.items()}                   
        EL = {level: [el['name'] for el in data] for level, data in level_data.items()}
        CL = {level: [el['name'] for el in data] for level, data in newLevel_data.items()}
        L = {level: EL.get(level, []) + CL.get(level, []) for level in set(EL.keys()).union(CL.keys())}
        L[0] = I # teste
        EL[0] = I # teste
        # considerando um custo maior do que o piso
        CE = {k: {team: 1.6*vals[1] for team, vals in ms.get(str(k), {}).items()} for k in K}
        
        D = {k: distance_data[k] for k in K}

        # Fixed generation of TC1, TC2, TC3 using dictionary comprehensions
        TC ={k: {i: {j: 0.5 for j in D[k][i].keys()} for i in D[k]} for k in K}
        FC = {1: {el: 350000 for el in L[1]},
              2: {el: 500000 for el in L[2]},
              3: {el: 700000 for el in L[3]}}

        W = {(d['NOME'], 1): d['QTDPESSOAS'] * 0.6 for d in demand_data}
        W.update({(d['NOME'], 2): d['QTDPESSOAS'] * 0.4 for d in demand_data})

        MS = {k: {team: vals[0] for team, vals in ms.get(str(k), {}).items()} for k in K}

        CNES = {k: cnes_data[k] for k in K}

        # cerca de 40% das pessoas tem alguma croninca
        ## a capacidae precisa ser altamente revisada no nivel 1
        # fazer com base em leitos disponiveis em cada local
        # para unidades novas colocar um valor fixo
        # 2315560.0/161 = 14.382,36
        # a capacidade é calculada sendo 10.000 + 416.67 * leitos esse numero foi tirado com base na qunatidade de leitos por habitante
        C = {# toda unidade que não estiver caalogada recebe o valor medio dos nivel
            k: {
                el: cap[f'{k}'][el] if el in cap[f'{k}'] else sum(cap[f'{k}'].values()) / len(cap[f'{k}'])
                for el in L[k]
            }
            for k in K
        }
        U = {1: 54, 2: 10, 3: 1}# maximo permit
        O = {k: {el: 0.6 if k==1 else 0.4 for el in L[k]} for k in range(1,len(K))}
        
        ##########################################
        # calculo de custo de atendimento
        # Não tenho dados para isso
        # 869319225.44 atenção basica -> 375,42 por pessoa
        # 1020903232,12 atemção secundaria e terciaria -> 2315560
        # não sei dizer se esses gastos estão unidos com os custo fixos + pessoal por ano
        # 1020903232/(2315560/0.8) =     
        VC = {  1: {(p, el): 375.42/12 for p in P for el in L[1]},
                2: {(p, el): 440.88/12 for p in P for el in L[2]},
                3: {(p, el): 440.88 for p in P for el in L[3]}}

        return {
            'I': I,
            'K': K,
            'P': P,
            'E': E,
            'EL': EL,
            'CL': CL,
            'L': L,
            'CE': CE,
            'D': D,
            'TC': TC,
            'VC': VC,
            'FC': FC,
            'W': W,
            'MS': MS,
            'CNES': CNES,
            'C': C,
            'U': U,
            'O': O,
        }

class Data_test:
    def get_data(self):
        return {
            'I': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            'K': [1, 2, 3],
            'P': [1, 2],
            'E': {
            1: ['ME1', 'EF1', 'ACS', 'DE1'],
            2: ['ME2', 'EF2', 'FON', 'OCD', 'DE2'],
            3: ['ME3', 'EF3', 'TE3', 'FIS', 'DE3']
            },
            'EL': {
            1: [1, 2, 3, 4, 5, 6],
            2: [1, 2, 3, 4],
            3: [1, 2, 3]
            },
            'CL': {
            1: [7, 8, 9, 10],
            2: [5, 6, 7, 8],
            3: [4, 5, 6]
            },
            'L': {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            2: [1, 2, 3, 4, 5, 6, 7, 8],
            3: [1, 2, 3, 4, 5, 6]
            },
            'CE1': {'ME1': 10, 'EF1': 10, 'ACS': 10, 'DE1': 10},
            'CE2': {'ME2': 20, 'EF2': 20, 'FON': 20, 'OCD': 20, 'DE2': 20},
            'CE3': {'ME3': 30, 'EF3': 30, 'TE3': 30, 'FIS': 30, 'DE3': 30},
            'D1': {i: {j: 1 for j in range(1, 11)}for i in range(1, 16) },
            'D2': {i: {j: 1  for j in range(1, 9)} for i in range(1, 11)},
            'D3': {i: {j: 1  for j in range(1, 7)}for i in range(1, 9)},
            'TC1': {i: {j: 1 for j in range(1, 11)} for i in range(1, 16) },
            'TC2': {i: {j: 1 for j in range(1, 9)} for i in range(1, 11) },
            'TC3': {i: {j: 1  for j in range(1, 7)} for i in range(1, 9)},
            'VC1': {(i,j): 5 for i in range(1, 3) for j in range(1, 11)},
            'VC2': {(i,j): 10 for i in range(1, 3) for j in range(1, 9)},
            'VC3': {(i,j): 20 for i in range(1, 3) for j in range(1, 7)},
            'FC1': {i: 1000 if i <= 6 else 100 for i in range(1, 11)},
            'FC2': {i: 200 for i in range(1, 9)},
            'FC3': {i: 300 for i in range(1, 7)},
            'W': {(i, j): 100 if j == 1 else 200 for i in range(1, 16) for j in range(1, 3)},
            'MS1': {'ME1': 0.02, 'EF1': 0.002, 'ACS': 0.002, 'DE1': 0.002},
            'MS2': {'ME2': 0.01, 'EF2': 0.01, 'FON': 0.01, 'OCD': 0.01, 'DE2': 0.01},
            'MS3': {'ME3': 0.01, 'EF3': 0.02, 'TE3': 0.01, 'FIS': 0.02, 'DE3': 0.01},
            'CNES1': {j: {e: 5 for e in ['ME1', 'EF1', 'ACS', 'DE1']} for j in range(1, 11)},
            'CNES2': {j: {e: 3 for e in ['ME2', 'EF2', 'FON', 'OCD', 'DE2']} for j in range(1, 9)},
            'CNES3': {j: {e: 2 for e in ['ME3', 'EF3', 'TE3', 'FIS', 'DE3']} for j in range(1, 7)},
            'C1': {
            (1, 1): 1000, (1, 2): 1000, (1, 3): 1000, (1, 4): 1000, (1, 5): 1000, (1, 6): 1000,
            (1, 7): 1000, (1, 8): 500, (1, 9): 500, (1, 10): 500,
            (2, 1): 1000, (2, 2): 1000, (2, 3): 1000, (2, 4): 1000, (2, 5): 1000, (2, 6): 1000,
            (2, 7): 1000, (2, 8): 500, (2, 9): 500, (2, 10): 500
            },
            'C2': {1: 1000,2: 100,3: 100,4: 200,5: 200,6: 200,7: 200,8: 200},
            'C3': {i: 300 for i in range(1, 7)},
            'U': {1: 4, 2: 3, 3: 2},
            'O1': {i: 0.4 for i in range(1, 11)},
            'O2': {i: 0.7 for i in range(1, 9)}
        }
if __name__ == "__main__":
    Data().get_data()