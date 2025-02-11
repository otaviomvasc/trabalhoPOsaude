import csv
import json
import os

# Caminhos existentes
csv_file = r"P.O Saude/data_excel/dados_instalacoes_saude.csv"
# ,dt_comp,uf_sigla,municipio_codigo,municipio_nome,cnes,nome_fantasia,tipo_estabelecimento,tipo_novo_estabelecimento,natureza_juridica_tipo,natureza_juridica,gestao,convenio_sus,instalacao_codigo,instalacao_nome,instalacao_tipo,qt_instalacao,qt_instalacao_leitos,status_estabelecimento,location

            # leitos = row["qt_instalacao_leitos"]

el1_file = "P.O Saude/dados_json/EL_1.json" 
el2_file = "P.O Saude/dados_json/EL_2.json"
el3_file = "P.O Saude/dados_json/EL_3.json"
'''
        "name": "CENTRO DE SAUDE CALIFORNIA",
        "id": "22 CENTRO DE SAUDE CALIFORNIA",
        "location": "POINT (-44.008252 -19.9231347)",
        "latitude": -19.9231347,
        "longitude": -44.008252,
        "type": "02 CENTRO DE SAUDE/UNIDADE BASICA"
'''
# Novo caminho para salvar o JSON combinado
output_json = "P.O Saude/dados_json/capacidade.json"
municipio_nome = "BELO HORIZONTE"  # Alterado para string


def contar_leitos_por_nivel():
    # Função auxiliar para carregar hospitais de um nível do JSON
    def load_hospitals(file):
        with open(file, encoding='utf-8') as jsonfile:
            # Assume que o arquivo é uma lista de objetos com chave "name"
            return { hosp["name"].strip().upper() for hosp in json.load(jsonfile) }
            
    hosp_el1 = load_hospitals(el1_file)
    hosp_el2 = load_hospitals(el2_file)
    hosp_el3 = load_hospitals(el3_file)
    
    # Inicializa agregadores para cada nível
    agg = {1: {}, 2: {}, 3: {}}
    target = municipio_nome.strip().upper()
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("municipio_nome", "").strip().upper() != target:
                continue
            hname = row.get("nome_fantasia", "").strip().upper()
            try:
                nleitos = int(row.get("qt_instalacao_leitos", "0"))
            except ValueError:
                nleitos = 0
            if hname in hosp_el1:
                agg[1][hname] = agg[1].get(hname, 0) + nleitos
            if hname in hosp_el2:
                agg[2][hname] = agg[2].get(hname, 0) + nleitos
            if hname in hosp_el3:
                agg[3][hname] = agg[3].get(hname, 0) + nleitos

    # Para hospitais presentes nos JSON mas não no CSV, define valor 0
    for hosp in hosp_el1:
        if hosp not in agg[1]:
            agg[1][hosp] = 0
    for hosp in hosp_el2:
        if hosp not in agg[2]:
            agg[2][hosp] = 0
    for hosp in hosp_el3:
        if hosp not in agg[3]:
            agg[3][hosp] = 0
                
    capacity_agg = {}
    for nivel, hospitais in agg.items():
        soma = 15000 
        mult = 1
        if nivel == 2:
            soma = 50000
            mult = 5
        if nivel == 3:
            soma = 50000
            mult = 5
        capacity_agg[nivel] = { hosp: soma + mult*416.67 * leitos for hosp, leitos in hospitais.items() }

    # Combina os resultados em um único dicionário
    # result = {"leitos": agg, "capacidade": capacity_agg}
    
    with open(output_json, "w", encoding="utf-8") as outjson:
        json.dump(capacity_agg, outjson, ensure_ascii=False, indent=2)
#2,4 leitos por 1000 habitantes
# 1000/2.4 = 416.67 habitantes por leito
if __name__ == "__main__":
    contar_leitos_por_nivel()
