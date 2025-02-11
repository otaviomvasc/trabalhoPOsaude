import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Caminhos dos arquivos
caminho_shp = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/MG_Setores_2020.shp"
caminho_fluxo = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/fluxo_shc_thc_glpk.csv"
caminho_shc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/localizacao_shc_coord_id.xlsx"
caminho_thc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/localizacao_thc_coord_id.xlsx"

# 🔹 Carregar o Shapefile e filtrar apenas Divinópolis
gdf = gpd.read_file(caminho_shp)
gdf = gdf[gdf["NM_MUN"] == "Divinópolis"]
gdf = gdf[gdf.is_valid]  # Garantir geometrias válidas

# 🔹 Carregar dados das SHCs
df_shc = pd.read_excel(caminho_shc)
df_shc[['lon', 'lat']] = df_shc['Coordenadas'].apply(eval).apply(pd.Series)
gdf_shc = gpd.GeoDataFrame(df_shc, geometry=gpd.points_from_xy(df_shc['lon'], df_shc['lat']))

# 🔹 Carregar dados das THCs
df_thc = pd.read_excel(caminho_thc)
df_thc[['lon', 'lat']] = df_thc['Coordenadas'].apply(eval).apply(pd.Series)
gdf_thc = gpd.GeoDataFrame(df_thc, geometry=gpd.points_from_xy(df_thc['lon'], df_thc['lat']))

# 🔹 Carregar dados de fluxo
df_fluxo = pd.read_csv(caminho_fluxo)

# 🔹 Criar o mapa
fig, ax = plt.subplots(figsize=(12, 12))

# 🔹 Plotar zonas censitárias no fundo
gdf.plot(ax=ax, color="#FFF9C4", edgecolor="black", linewidth=0.5)  # Zonas censitárias em amarelo claro

# 🔹 Adicionar SHCs como triângulos azuis
gdf_shc.plot(ax=ax, marker="^", color="green", markersize=3, label="SHCs")

# 🔹 Adicionar THCs como triângulos verdes
gdf_thc.plot(ax=ax, marker="^", color="red", markersize=3, label="THCs")

# 🔹 Adicionar linhas de fluxo entre SHCs e THCs
for _, row in df_fluxo.iterrows():
    shc_info = gdf_shc[gdf_shc["ID"] == row["SHC"]]
    thc_info = gdf_thc[gdf_thc["ID"] == row["THC"]]

    if not shc_info.empty and not thc_info.empty:
        x_shc, y_shc = shc_info.geometry.x.iloc[0], shc_info.geometry.y.iloc[0]
        x_thc, y_thc = thc_info.geometry.x.iloc[0], thc_info.geometry.y.iloc[0]

        ax.plot([x_shc, x_thc], [y_shc, y_thc], color="black", linewidth=0.3, alpha=0.7)

# 🔹 Ajustar título e legendas
ax.set_title("Fluxo entre SHCs e THCs em Divinópolis", fontsize=16)

# 🔹 Criar legenda
legend_elements = [
    Patch(facecolor="#FFF9C4", edgecolor="black", label="Zonas Censitárias"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="green", markersize=10, label="SHCs"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="red", markersize=10, label="THCs"),
    Line2D([0], [0], color="black", linewidth=2, label="Linhas de Fluxo")
]
ax.legend(handles=legend_elements, loc="upper left")

# 🔹 Remover eixos para visualização mais limpa
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# 🔹 Salvar o mapa em alta resolução
output_path = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/mapa_fluxo_shc_thc.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"\n✅ Mapa salvo com sucesso em: {output_path}")

# 🔹 Exibir o mapa
plt.show()
