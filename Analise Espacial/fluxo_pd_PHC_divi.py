import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Caminhos dos arquivos
caminho_shp = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/MG_Setores_2020.shp"
caminho_xlsx = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/id_zonas_censitarias.xlsx"
caminho_fluxo = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/fluxo_glpk.csv"
caminho_ubs = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/localizacao_esf_coord_id.xlsx"

# 🔹 Carregar o Shapefile e filtrar apenas Divinópolis
gdf = gpd.read_file(caminho_shp)
gdf = gdf[gdf["NM_MUN"] == "Divinópolis"]
gdf = gdf[gdf.is_valid]  # Garantir geometrias válidas

# 🔹 Criar um mapeamento entre os índices do Shapefile e os `CD_SETOR`
gdf = gdf.sort_values("CD_SETOR").reset_index(drop=True)
gdf["ID_FLUXO"] = gdf.index + 1  # Criar ID de 1 a 524

# 🔹 Carregar os dados auxiliares (população e área)
df_aux = pd.read_excel(caminho_xlsx, decimal=',')
df_aux["CD_SETOR"] = df_aux["CD_SETOR"].astype(str).str.rstrip("P")
gdf["CD_SETOR"] = gdf["CD_SETOR"].astype(str)

# 🔹 Mesclar os dados auxiliares no Shapefile
gdf = gdf.merge(df_aux[["CD_SETOR"]], on="CD_SETOR", how="left")

# 🔹 Criar o mapeamento do fluxo (IDs do fluxo → `CD_SETOR`)
mapeamento_fluxo = dict(zip(gdf["ID_FLUXO"], gdf["CD_SETOR"]))

# 🔹 Carregar os dados de fluxo e ajustar os IDs
df_fluxo = pd.read_csv(caminho_fluxo)
df_fluxo["CD_SETOR"] = df_fluxo["PontoDemanda"].map(mapeamento_fluxo)

# 🔹 Carregar os dados das PHCs e converter coordenadas
df_ubs = pd.read_excel(caminho_ubs)
df_ubs[['lon', 'lat']] = df_ubs['Coordenadas'].apply(eval).apply(pd.Series)

# 🔹 Criar um GeoDataFrame para as PHCs
gdf_ubs = gpd.GeoDataFrame(df_ubs, geometry=gpd.points_from_xy(df_ubs['lon'], df_ubs['lat']))

# 🔹 Criar o mapa
fig, ax = plt.subplots(figsize=(12, 12))

# 🔹 Plotar zonas censitárias no mapa
gdf.plot(ax=ax, color="#FFF9C4", edgecolor="black", linewidth=0.5)  # Zonas censitárias em amarelo claro

# 🔹 Adicionar centroides como bolinhas pretas
for _, row in gdf.iterrows():
    centroid = row.geometry.centroid
    ax.scatter(centroid.x, centroid.y, marker="o", color="black", s=0.5)  # Bolinhas pretas

# 🔹 Adicionar linhas de fluxo em preto
for _, row in df_fluxo.iterrows():
    zona = gdf[gdf["CD_SETOR"] == row["CD_SETOR"]]
    ubs_info = gdf_ubs[gdf_ubs["ID"] == row["PHC"]]

    if not zona.empty and not ubs_info.empty:
        x_zona, y_zona = zona.geometry.centroid.x.iloc[0], zona.geometry.centroid.y.iloc[0]
        x_ubs, y_ubs = ubs_info.geometry.x.iloc[0], ubs_info.geometry.y.iloc[0]

        ax.plot([x_zona, x_ubs], [y_zona, y_ubs], color="black", linewidth=0.3, alpha=0.7)  # Linha de fluxo preta

# 🔹 Adicionar PHCs como triângulos azuis
ax.scatter(gdf_ubs["lon"], gdf_ubs["lat"], marker="^", color="blue", s=3, label="PHCs")  # Triângulo vermelho

# 🔹 Ajustar título e legendas
ax.set_title("Fluxo das Zonas Censitárias para as PHCs em Divinópolis", fontsize=16)

# 🔹 Criar legenda à esquerda
legend_elements = [
    Patch(facecolor="#FFF9C4", edgecolor="black", label="Zonas Censitárias"),
    Line2D([0], [0], color="black", linewidth=2, label="Linhas de Fluxo"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="blue", markersize=10, label="PHCs")
]
ax.legend(handles=legend_elements, loc="upper left")

# 🔹 Remover eixos para visualização mais limpa
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# 🔹 Salvar o mapa em alta resolução
output_path = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/mapa_fluxo_ajustado.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"\n✅ Mapa salvo com sucesso em: {output_path}")

# 🔹 Exibir o mapa
plt.show()
