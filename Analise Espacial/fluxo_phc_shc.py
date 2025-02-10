import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Caminhos dos arquivos
caminho_shp = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/MG_Setores_2020.shp"
caminho_xlsx = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/id_zonas_censitarias.xlsx"
caminho_fluxo = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/fluxo_phc_shc_glpk.csv"
caminho_ubs = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/localizacao_esf_coord_id.xlsx"
caminho_shc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/localizacao_shc_coord_id.xlsx"

# 🔹 Carregar o Shapefile e filtrar apenas Divinópolis
gdf = gpd.read_file(caminho_shp)
gdf = gdf[gdf["NM_MUN"] == "Divinópolis"]
gdf = gdf[gdf.is_valid]  # Garantir geometrias válidas

# 🔹 Carregar dados auxiliares (população e área)
df_aux = pd.read_excel(caminho_xlsx, decimal=',')
df_aux["CD_SETOR"] = df_aux["CD_SETOR"].astype(str).str.rstrip("P")
gdf["CD_SETOR"] = gdf["CD_SETOR"].astype(str)
gdf = gdf.merge(df_aux[["CD_SETOR"]], on="CD_SETOR", how="left")

# 🔹 Carregar dados das PHCs
df_phc = pd.read_excel(caminho_ubs)
df_phc[['lon', 'lat']] = df_phc['Coordenadas'].apply(eval).apply(pd.Series)
gdf_phc = gpd.GeoDataFrame(df_phc, geometry=gpd.points_from_xy(df_phc['lon'], df_phc['lat']))

# 🔹 Carregar dados das SHCs
df_shc = pd.read_excel(caminho_shc)
df_shc[['lon', 'lat']] = df_shc['Coordenadas'].apply(eval).apply(pd.Series)
gdf_shc = gpd.GeoDataFrame(df_shc, geometry=gpd.points_from_xy(df_shc['lon'], df_shc['lat']))

# 🔹 Carregar dados de fluxo
df_fluxo = pd.read_csv(caminho_fluxo)

# 🔹 Criar o mapa
fig, ax = plt.subplots(figsize=(12, 12))

# 🔹 Plotar zonas censitárias no fundo
gdf.plot(ax=ax, color="#FFF9C4", edgecolor="black", linewidth=0.5)  # Zonas censitárias em amarelo claro

# 🔹 Adicionar PHCs como triângulos azuis
gdf_phc.plot(ax=ax, marker="^", color="blue", markersize=3, label="PHCs")

# 🔹 Adicionar SHCs como triângulos verdes
gdf_shc.plot(ax=ax, marker="^", color="green", markersize=3, label="SHCs")

# 🔹 Adicionar linhas de fluxo entre PHCs e SHCs
for _, row in df_fluxo.iterrows():
    phc_info = gdf_phc[gdf_phc["ID"] == row["PHC"]]
    shc_info = gdf_shc[gdf_shc["ID"] == row["SHC"]]

    if not phc_info.empty and not shc_info.empty:
        x_phc, y_phc = phc_info.geometry.x.iloc[0], phc_info.geometry.y.iloc[0]
        x_shc, y_shc = shc_info.geometry.x.iloc[0], shc_info.geometry.y.iloc[0]

        ax.plot([x_phc, x_shc], [y_phc, y_shc], color="black", linewidth=0.3, alpha=0.7)

# 🔹 Ajustar título e legendas
ax.set_title("Fluxo entre PHCs e SHCs em Divinópolis", fontsize=16)

# 🔹 Criar legenda
legend_elements = [
    Patch(facecolor="#FFF9C4", edgecolor="black", label="Zonas Censitárias"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="blue", markersize=10, label="PHCs"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="green", markersize=10, label="SHCs"),
    Line2D([0], [0], color="black", linewidth=2, label="Linhas de Fluxo")
]
ax.legend(handles=legend_elements, loc="upper left")

# 🔹 Remover eixos para visualização mais limpa
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# 🔹 Salvar o mapa em alta resolução
output_path = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/mapa_fluxo_phc_shc.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"\n✅ Mapa salvo com sucesso em: {output_path}")

# 🔹 Exibir o mapa
plt.show()
