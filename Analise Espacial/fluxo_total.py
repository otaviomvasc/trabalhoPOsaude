import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Caminhos dos arquivos
caminho_shp = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/MG_Setores_2020.shp"
caminho_xlsx = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/id_zonas_censitarias.xlsx"
caminho_fluxo_pd_phc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/fluxo_glpk.csv"
caminho_phc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/localizacao_esf_coord_id.xlsx"
caminho_shc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/localizacao_shc_coord_id.xlsx"
caminho_thc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/localizacao_thc_coord_id.xlsx"
caminho_fluxo_phc_shc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/fluxo_phc_shc_glpk.csv"
caminho_fluxo_shc_thc = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/fluxo_shc_thc_glpk.csv"

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
df_fluxo_pd_phc = pd.read_csv(caminho_fluxo_pd_phc)
df_fluxo_pd_phc["CD_SETOR"] = df_fluxo_pd_phc["PontoDemanda"].map(mapeamento_fluxo)
df_fluxo_phc_shc = pd.read_csv(caminho_fluxo_phc_shc)
df_fluxo_shc_thc = pd.read_csv(caminho_fluxo_shc_thc)

# 🔹 Carregar os dados das PHCs e converter coordenadas
df_phc = pd.read_excel(caminho_phc)
df_phc[['lon', 'lat']] = df_phc['Coordenadas'].apply(eval).apply(pd.Series)
gdf_phc = gpd.GeoDataFrame(df_phc, geometry=gpd.points_from_xy(df_phc['lon'], df_phc['lat']))

# 🔹 Carregar os dados das SHCs e THCs
df_shc = pd.read_excel(caminho_shc)
df_shc[['lon', 'lat']] = df_shc['Coordenadas'].apply(eval).apply(pd.Series)
gdf_shc = gpd.GeoDataFrame(df_shc, geometry=gpd.points_from_xy(df_shc['lon'], df_shc['lat']))

df_thc = pd.read_excel(caminho_thc)
df_thc[['lon', 'lat']] = df_thc['Coordenadas'].apply(eval).apply(pd.Series)
gdf_thc = gpd.GeoDataFrame(df_thc, geometry=gpd.points_from_xy(df_thc['lon'], df_thc['lat']))

# 🔹 Criar a figura com dois subplots
fig, axes = plt.subplots(1, 2, figsize=(20, 10), sharex=True, sharey=True)

# 🔹 Mapa 1: Com Zonas Censitárias
ax1 = axes[0]
gdf.plot(ax=ax1, color="#FFF9C4", edgecolor="black", linewidth=0.5)  # Zonas censitárias em amarelo claro
gdf_phc.plot(ax=ax1, marker="^", color="red", markersize=3, label="PHCs")
gdf_shc.plot(ax=ax1, marker="^", color="blue", markersize=3, label="SHCs")
gdf_thc.plot(ax=ax1, marker="^", color="green", markersize=3, label="THCs")

# Adicionar centroides como bolinhas pretas
gdf.centroid.plot(ax=ax1, color="black", markersize=0.5, label="Centroides")

# 🔹 Mapa 2: Apenas Estrutura de Fluxo
ax2 = axes[1]

gdf_phc.plot(ax=ax2, marker="^", color="red", markersize=3, label="PHCs")
gdf_shc.plot(ax=ax2, marker="^", color="blue", markersize=3, label="SHCs")
gdf_thc.plot(ax=ax2, marker="^", color="green", markersize=3, label="THCs")
gdf.centroid.plot(ax=ax2, color="black", markersize=0.5, label="Centroides")
# Adicionar fluxos PD → PHC
for _, row in df_fluxo_pd_phc.iterrows():
    zona_info = gdf[gdf["CD_SETOR"] == row["CD_SETOR"]]
    phc_info = gdf_phc[gdf_phc["ID"] == row["PHC"]]
    if not zona_info.empty and not phc_info.empty:
        x_zona, y_zona = zona_info.geometry.centroid.x.iloc[0], zona_info.geometry.centroid.y.iloc[0]
        x_phc, y_phc = phc_info.geometry.x.iloc[0], phc_info.geometry.y.iloc[0]
        ax1.plot([x_zona, x_phc], [y_zona, y_phc], color="black", linewidth=0.3, alpha=0.7)
        ax2.plot([x_zona, x_phc], [y_zona, y_phc], color="black", linewidth=0.3, alpha=0.7)

# 🔹 Adicionar fluxos PHC → SHC
for _, row in df_fluxo_phc_shc.iterrows():
    phc_info = gdf_phc[gdf_phc["ID"] == row["PHC"]]
    shc_info = gdf_shc[gdf_shc["ID"] == row["SHC"]]
    if not phc_info.empty and not shc_info.empty:
        ax1.plot([phc_info.geometry.x.iloc[0], shc_info.geometry.x.iloc[0]],
                 [phc_info.geometry.y.iloc[0], shc_info.geometry.y.iloc[0]],
                 color="black", linewidth=0.3, alpha=0.7)
        ax2.plot([phc_info.geometry.x.iloc[0], shc_info.geometry.x.iloc[0]],
                 [phc_info.geometry.y.iloc[0], shc_info.geometry.y.iloc[0]],
                 color="blue", linewidth=0.3, alpha=0.7)

# 🔹 Adicionar fluxos SHC → THC
for _, row in df_fluxo_shc_thc.iterrows():
    shc_info = gdf_shc[gdf_shc["ID"] == row["SHC"]]
    thc_info = gdf_thc[gdf_thc["ID"] == row["THC"]]
    if not shc_info.empty and not thc_info.empty:
        ax1.plot([shc_info.geometry.x.iloc[0], thc_info.geometry.x.iloc[0]],
                 [shc_info.geometry.y.iloc[0], thc_info.geometry.y.iloc[0]],
                 color="black", linewidth=0.3, alpha=0.7)
        ax2.plot([shc_info.geometry.x.iloc[0], thc_info.geometry.x.iloc[0]],
                 [shc_info.geometry.y.iloc[0], thc_info.geometry.y.iloc[0]],
                 color="green", linewidth=0.3, alpha=0.7)

ax1.set_title("Fluxo Completo com Zonas Censitárias", fontsize=16)
ax2.set_title("Apenas Estrutura de Fluxo", fontsize=16)

# 🔹 Ajustar legenda
legend_elements = [
    Patch(facecolor="#FFF9C4", edgecolor="black", label="Zonas Censitárias"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="red", markersize=5, label="PHCs"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="blue", markersize=5, label="SHCs"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="green", markersize=5, label="THCs"),
    Line2D([0], [0], color="black", linewidth=1, label="Linhas de Fluxo")
]
ax1.legend(handles=legend_elements, loc="upper left")

# 🔹 Salvar o mapa
output_path = "C:/Users/bmmor/Desktop/Doutorado UFMG/Analise Espacial/mapa_fluxo_total.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

# 🔹 Exibir o mapa
plt.show()
