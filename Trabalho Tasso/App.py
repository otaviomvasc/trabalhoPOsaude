# import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
# import dash_leaflet.express as dlx
from dash import Dash, html, Output, Input
from dash_extensions.javascript import assign
import json
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from shapely.geometry import Point
from matplotlib.colors import PowerNorm
from shapely import wkt  # added import



class Create_Map:
    def __init__(self, urljson: str):
        with open(urljson, encoding="utf-8") as f:
            self.data = gpd.GeoDataFrame(json.load(f))
        if "GEOMETRIA" in self.data.columns:
            # Modified: Create geometry Series and pass it explicitly to GeoDataFrame
            geometry = self.data["GEOMETRIA"].apply(wkt.loads)
            self.data = gpd.GeoDataFrame(self.data, geometry=geometry)
        elif "longitude" in self.data.columns and "latitude" in self.data.columns:
            
            # Modified: Create geometry Series and pass it explicitly to GeoDataFrame
            geometry = self.data.apply(lambda row: Point(row["longitude"], row["latitude"]), axis=1)
            self.data = gpd.GeoDataFrame(self.data, geometry=geometry)
        else:
            raise AttributeError("No geometry data found. Provide 'GEOMETRIA' or 'longitude' and 'latitude' columns.")
        bounds = self.data.total_bounds
        self.center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
        self.bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
        self.App()
    def Color(self):
        min = self.data['QTDPESSOAS'].min()
        max = self.data['QTDPESSOAS'].max()
        norm = PowerNorm(gamma=0.1, vmin=min, vmax=max)  # Ajuste o valor de gamma conforme necessário
        # color = lambda cor: mcolors.to_hex(plt.get_cmap('viridis')(norm(cor)))
        color = lambda cor: mcolors.to_hex(plt.get_cmap('Blues')(norm(cor)))
        self.data['color'] = self.data['QTDPESSOAS'].apply(lambda x: color(x))
    def GeoJSON(self):
        self.Color()
        style_handle = assign("""
            function(feature, context) {
                return {
                    weight: 2,
                    opacity: 0,        
                    color: 'white',
                    dashArray: '1',
                    fillOpacity: 0,     
                    fillColor: feature.properties['color']
                };
            }
        """)
        return dl.GeoJSON(
            data=json.loads(self.data.to_json()),
            style=style_handle,
            zoomToBounds=True,
            zoomToBoundsOnClick=True,
            hoverStyle={"weight": 1, "color": '#666', "dashArray": ''},
            id="geojson"
            )
    def Info(self,feature=None):
    # Função para gerar as informações a serem exibidas no popup
        def get_info(feature=None):
            header = [html.H4("População por Bairro")]
            if not feature:
                return header + [html.P("Passe o mouse sobre um bairro")]
            bairro      = feature["properties"]["NOME"]
            qtd_pessoas = feature["properties"]["QTDPESSOAS"]
            return header + [html.B(bairro), html.Br(), f"{qtd_pessoas} pessoas"]
        
        return html.Div(children=get_info(feature), id="info", className="info", 
                        style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"})
    def App(self):
        # Criar o aplicativo Dash
        app = Dash(__name__)
        app.layout = html.Div([
            dl.Map(
                children=[
                    dl.TileLayer(),
                    self.GeoJSON(),
                    self.Info(),
                    dl.Pane(id="flowPane", name="flowPane", style={"zIndex": 650})  # Custom pane for flows with required 'name'
                ], 
                center=self.center,  # Centro do mapa
                minZoom=11.4,  # Zoom mínimo permitido
                bounds=self.bounds,  # Limitar navegação
                maxBounds=self.bounds,  # Limitar navegação
                maxBoundsViscosity=0.1,  # Rigor na limitação
                worldCopyJump=False,  # Impedir cópias do mapa ao atravessar o meridiano
                style={'width': '100%', 'height': '600px'}  # Estilo do mapa
            )
        ])
        self.app = app
        self.register_callbacks()

    def add_markers(self, file: json, level: str):

        LEVEL = {
            "1": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
            "2": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png",
            "3": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
            "4": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
            "5": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png",
            "6": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png"
        }
        markers = []
        for marker in file:
            m = dl.Marker(
                position=[marker["latitude"], marker["longitude"]],
                icon={
                    "iconUrl": LEVEL.get(level),
                    "iconSize": [20, 33],   # Reduced marker size
                    "iconAnchor": [10, 33]  # Alignment for the reduced icon
                },
                children=[
                    dl.Tooltip(marker["name"]),
                    dl.Popup([
                        html.H4(marker["name"])
                        # ...additional marker info if needed...
                    ])
                ]
            )
            markers.append(m)
        self.app.layout.children[0].children.append(dl.LayerGroup(markers))
        

    def register_callbacks(self):
        @self.app.callback(Output("info", "children"), Input("geojson", "hoverData"))
        def info_hover(feature):
            return self.Info(feature).children

    def add_flow_lines(self):
        with open("flow_results.json", encoding="utf-8") as f:
            flows = json.load(f)
        
        marker_data = {}
        for lvl in ["1", "2", "3"]:
            file = f"P.O Saude/dados_json/EL_{lvl}.json"
            with open(file, encoding='utf-8') as f:
                markers = json.load(f)
            marker_data[lvl] = {m["name"]: [m["latitude"], m["longitude"]] for m in markers}
        
        # Load new markers for levels "4", "5", "6" (mapped from new_locations.json)
        new_unit_map = {"1": "4", "2": "5", "3": "6"}
        try:
            with open("new_locations.json", encoding="utf-8") as f:
                saved_names = json.load(f)
        except:
            saved_names = {}
        for key, new_level in new_unit_map.items():
            names = saved_names.get(key, [])
            if names:
                coord_file = f"P.O Saude/dados_json/novas_unidades_nivel_{key}.json"
                with open(coord_file, encoding="utf-8") as f:
                    new_markers = json.load(f)
                filtered = [m for m in new_markers if m["name"] in names]
                marker_data[new_level] = {m["name"]: [m["latitude"], m["longitude"]] for m in filtered}
            else:
                marker_data[new_level] = {}
        
        # Build polygon centroids dict from self.data (assuming property "NOME")
        polygon_centroids = {}
        for _, row in self.data.iterrows():
            centroid = [row.geometry.centroid.y, row.geometry.centroid.x]
            polygon_centroids[row["NOME"]] = centroid
        
        # Compute maximum flow value for scaling line weight
        all_flow_vals = [flow 
                         for flows_by_source in flows.values()
                         for destinations in flows_by_source.values()
                         for flow in destinations.values()]
        max_flow = max(all_flow_vals) if all_flow_vals else 1
        
        # Color mapping for each flow level
        color_map = {"1": "green", "2": "yellow", "3": "red"}
        
        flow_lines = []
        # Iterate over each k-level flow and use fallback lookups for new units
        for k, flows_by_source in flows.items():
            for source_name, destinations in flows_by_source.items():
                for dest_name, flow_val in destinations.items():
                    if k == "1":
                        src = polygon_centroids.get(source_name)
                        dst = marker_data.get("1", {}).get(dest_name) or marker_data.get("4", {}).get(dest_name)
                    elif k == "2":
                        src = marker_data.get("1", {}).get(source_name) or marker_data.get("4", {}).get(source_name)
                        dst = marker_data.get("2", {}).get(dest_name) or marker_data.get("5", {}).get(dest_name)
                    elif k == "3":
                        src = marker_data.get("2", {}).get(source_name) or marker_data.get("5", {}).get(source_name)
                        dst = marker_data.get("3", {}).get(dest_name) or marker_data.get("6", {}).get(dest_name)
                    else:
                        continue
                    if src and dst:
                        # Weight proportional to flow value
                        weight = 2 + (flow_val / max_flow) * 8
                        line = dl.Polyline(
                            positions=[src, dst],
                            color=color_map.get(k, "blue"),
                            weight=weight,
                            opacity=1,
                            pane="flowPane",   # Specify pane so flows are drawn on top
                            children=[dl.Tooltip(f"Flow: {flow_val}")]
                        )
                        flow_lines.append(line)
        flows_layer = dl.LayerGroup(flow_lines)
        self.app.layout.children[0].children.append(flows_layer)

    def run(self):
        self.app.run_server(debug=True)

if __name__ == "__main__":
    mapa = Create_Map("P.O Saude/dados_json/bairro_demanda_set.json")
    for level in ["1", "2", "3"]:
        file = f"P.O Saude/dados_json/EL_{level}.json"
        with open(file, 'r', encoding='utf-8') as f:
            markers_data = json.load(f)
        mapa.add_markers(markers_data, level)

    
    with open("new_locations.json", encoding='utf-8') as f:
        saved_names = json.load(f)  # keys: "1", "2", "3"
    # Map new_locations keys to marker levels: "1"->"4", "2"->"5", "3"->"6"
    marker_level_map = {"1": "4", "2": "5", "3": "6"}
    for level_key, names in saved_names.items():
        if names:
            # Load the corresponding coordinate file
            coord_file = f"P.O Saude/dados_json/novas_unidades_nivel_{level_key}.json"
            with open(coord_file, encoding='utf-8') as f:
                coord_markers = json.load(f)  # Expecting list of dicts with keys: name, latitude, longitude
            # Filter markers to add only those with names in saved_names
            filtered_markers = [m for m in coord_markers if m["name"] in names]
            if filtered_markers:
                mapa.add_markers(filtered_markers, marker_level_map.get(level_key))
                
    # Add flow lines for flows defined in flow_results.json
    mapa.add_flow_lines()
    
    mapa.run()