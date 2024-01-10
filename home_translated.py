import dash
import json
#from jupyter_dash import JupyterDash

import dash_bootstrap_components as dbc
import dash_leaflet as dl
import geopandas as gpd
import ursa.utils.raster as ru

from dash import callback, html, Input, Output, State
from pathlib import Path
from shapely.geometry import shape
from ursa.utils.geometry import geometry_to_json, hash_geometry

translations = {
    "Bienvenido": {
        "es": "Bienvenido",
        "en": "Welcome",
        "pt": "Bem-vindo",
    },
    "Instrucciones": {
        "es": "Esta aplicación web le permitirá explorar el crecimiento histórico y futuro de su ciudad.",
        "en": "This web application will allow you to explore the historical and future growth of your city.",
        "pt": "Este aplicativo web permitirá que você explore o crescimento histórico e futuro de sua cidade.",
    },
        
    "Seleccione_pais": {
        "es": "Por favor seleccione un país y ciudad en los menús de abajo.",
        "en": "Please select a country and city from the menus below.",
        "pt": "Por favor, selecione um país e uma cidade nos menus abaixo.",
    },
    "Elegida_ciudad": {
        "es": "Una vez elegida la ciudad puede explorar las visualizaciones en la barra de navegación a la izquierda.",
        "en": "Once you have chosen the city, you can explore the visualizations on the left navigation bar.",
        "pt": "Depois de escolher a cidade, você pode explorar as visualizações na barra de navegação à esquerda.",
    },
    "Seleccionar": {
        "es": "Seleccionar",
        "en": "Select",
        "pt": "Selecionar",
    },
    "Bounding_box": {
        "es": "El bounding box por defecto utiliza los límites de zonas metropolitanas que identifica Global Human Settlement Layer (GHSL). Le recomendamos utilizar estos. Si quiere modificar el área de análisis para ampliarla o reducirla, utilice los botones de la derecha. Cuando haya terminado de seleccionar su área de interés, presione el botón de Aplicar.",
        "en": "The default bounding box uses the limits of metropolitan areas identified by the Global Human Settlement Layer (GHSL). We recommend using these. If you want to modify the analysis area to expand or reduce it, use the buttons on the right. When you have finished selecting your area of interest, press the Apply button.",
        "pt": "A caixa delimitadora padrão utiliza os limites das áreas metropolitanas identificadas pela Camada Global de Assentamento Humano (GHSL). Recomendamos usar esses limites. Se desejar modificar a área de análise para ampliar ou reduzir, use os botões à direita. Quando terminar de selecionar sua área de interesse, pressione o botão Aplicar.",
    },
    "Region_original": {
        "es": "Si desea utilizar la región original, borre todas las regiones personalizadas y presione Aplicar.",
        "en": "If you want to use the original region, delete all custom regions and press Apply.",
        "pt": "Se desejar usar a região original, exclua todas as regiões personalizadas e pressione Aplicar.",
    },
    "Aplicar": {
        "es": "Aplicar",
        "en": "Apply",
        "pt": "Aplicar",
    },
    "No_proveyo": {
        "es": "No se proveyó ninguna región personalizada. Se utilizará la original.",
        "en": "No custom region was provided. The original will be used.",
        "pt": "Nenhuma região personalizada foi fornecida. A original será usada.",
    },
    "Region_personalizada": {
        "es": "La región personalizada provista no está contenida en la original.",
        "en": "The provided custom region is not contained in the original.",
        "pt": "A região personalizada fornecida não está contida na original.",
    },
    "Mas_de_una_region": {
        "es": "Más de una región personalizada provista. Se tomará una al azar.",
        "en": "More than one custom region provided. One will be taken at random.",
        "pt": "Mais de uma região personalizada fornecida. Uma será escolhida ao acaso.",
    },
}


dash.register_page(__name__, path="/")

PATH_FUA = Path("./data/output/cities/")

cities_fua = gpd.read_file("./data/output/cities/cities_fua.gpkg")
cities_uc = gpd.read_file("./data/output/cities/cities_uc.gpkg")
with open("./data/output/cities/cities_by_country.json", "r", encoding="utf8") as f:
    cities_by_country = json.load(f)

DROPDOWN_STYLE = {
    "color": "gray",
    "width": "67%",
    "margin": "10px auto",
    "font-size": "1.125rem",
}

BUTTON_STYLE = {"margin": "10px auto", "width": "fit-content"}


country_dropdown = dbc.Select(
    options=[
        {"label": country, "value": country} for country in cities_fua.country.unique()
    ],
    value="Argentina",
    id="dropdown-country",
    style=DROPDOWN_STYLE,
    persistence=True,
    persistence_type="session",
)

city_dropdown = dbc.Select(
    id="dropdown-city",
    style=DROPDOWN_STYLE,
    persistence=True,
    persistence_type="session",
)

language_buttons = dbc.ButtonGroup(
    [
        dbc.Button("Español", id="btn-lang-es", n_clicks=0),
        dbc.Button("English", id="btn-lang-en", n_clicks=0),
        dbc.Button("Portuguese", id="btn-lang-pt", n_clicks=0),
    ],
    style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1"},
)


def translate_text(text_id, language):
    return translations.get(text_id, {}).get(language, "")

layout = html.Div(
    [
        dbc.Alert(
            id="global-custom-region-alert",
            is_open=False,
            color="danger",
            dismissable=True,
        ),
        #navbar,
        language_buttons,
        html.H1(id="welcome-text", children=translate_text("Bienvenido", "es")), # Traduccion
        html.P(id="instructions-text", children=translate_text("Instrucciones", "es")), # Traduccion
        html.Div(
            [
         #       html.P(
         #           id="instructions-text", children=translate_text("Instrucciones", "es"),
         #           id="instructions-text2", children=translate_text("Instrucciones2", "es"),
        #        ),
                html.P(id="Seleccione_pais-text", children=translate_text("Seleccione_pais", "es")),
                html.P(id="Elegida_ciudad-text", children=translate_text("Elegida_ciudad", "es")),
            ]
        ),
        html.Div(
            [
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(country_dropdown, width=4),
                                dbc.Col(city_dropdown, width=4),
                            ],
                            justify="center",
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Button(id="btn-country-select", children=translate_text("Seleccionar", "es"),
                                           class_name="text-center"),
                                #class_name="text-center",
                            )
                        ),
                    ]
                ),
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dl.Map(
                                        [
                                            dl.TileLayer(),
                                            dl.FeatureGroup(
                                                children=dl.EditControl(
                                                    id="global-edit-control",
                                                    position="topright",
                                                    draw=dict(
                                                        circle=False,
                                                        line=False,
                                                        polyline=False,
                                                        rectangle=True,
                                                        polygon=False,
                                                        marker=False,
                                                        circlemarker=False,
                                                    ),
                                                    edit=dict(remove=True),
                                                ),
                                                id="global-feature-group",
                                            ),
                                            dl.Rectangle(
                                                bounds=[[0, 0], [1, 0]],
                                                id="global-polygon",
                                            ),
                                        ],
                                        style={"height": "70vh"},
                                        center=[-5, -80],
                                        zoom=4,
                                        id="global-map",
                                        className="my-2",
                                    ),
                                    width=10,
                                ),
                                dbc.Col(
                                    html.Div(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    html.P(id="Bounding_box-text", 
                                                           children=translate_text("Bounding_box", "es")),
                                                    
                                                    #html.P(
                                                     #   [
                                                      #      html.B("Aplicar"),
                                                       #     ".",
                                                       # ],
                                                       # style={"text-align": "start"},
                                                    #)
                                                ),
                                                class_name="supp-info",
                                            ),
                                            dbc.Card(
                                                dbc.CardBody(
                                                    html.P(id="Region_original-text", 
                                                           children=translate_text("Region_original", "es")),
                               
                                                   # html.P(
                                                   #     [
                                                    #        "Si desea utilizar la región original, borre todas las regiones personalizadas y presione ",
                                                     #       html.B("Aplicar"),
                                                      #      ".",
                                                       # ],
                                                        #style={"text-align": "start"},
                                                    #)
                                                ),
                                                class_name="supp-info",
                                            ),
                                            dbc.Button(
                                                id="global-btn-apply-region", 
                                                children=translate_text("Aplicar", "es"),
                                            ),
                                        ],
                                        style={"text-align": "center"},
                                    ),
                                    width=2,
                                ),
                            ],
                            justify="center",
                        ),
                    ]
                ),
            ]
        ),
    ]
)

@callback(
    Output("welcome-text", "children"), 
     Output("instructions-text", "children"),
     Output("Seleccione_pais-text", "children"),
     Output("Elegida_ciudad-text", "children"),
     Output("Bounding_box-text", "children"),
     Output("Region_original-text", "children"),
    Output("btn-country-select", "children"),
    Output("global-btn-apply-region", "children"),
    
    
    [Input("btn-lang-es", "n_clicks"), Input("btn-lang-en", "n_clicks"), Input("btn-lang-pt", "n_clicks")],
    prevent_initial_call=True,
)
def change_language(btn_es, btn_en, btn_pt):
    # Determina cuál botón se hizo clic más recientemente
    ctx = dash.callback_context
    button_id = ctx.triggered_id.split(".")[0]

    # Obtiene el idioma correspondiente al botón clicado
    if button_id == "btn-lang-es":
        language = "es"
    elif button_id == "btn-lang-en":
        language = "en"
    elif button_id == "btn-lang-pt":
        language = "pt"
    else:
        # Si no hay clic en botones de idioma, usa el idioma predeterminado (español)
        language = "es"

    # Retorna los textos traducidos
    welcome_text = translate_text("Bienvenido", language)
    instructions_text = translate_text("Instrucciones", language)
    Seleccione_pais_text = translate_text("Seleccione_pais", language)
    Elegida_ciudad_text = translate_text("Elegida_ciudad", language)
    Bounding_box_text = translate_text("Bounding_box", language)
    Region_original_text = translate_text("Region_original", language)
    
    Seleccionar_text = translate_text("Seleccionar", language)
    Aplicar_text = translate_text("Aplicar", language)
    
    return (
        welcome_text,
        instructions_text,
        Seleccione_pais_text,
        Elegida_ciudad_text,
        Bounding_box_text,
        Region_original_text,
        Seleccionar_text,
        Aplicar_text
           )


@callback(
    Output("dropdown-city", "options"),
    Output("dropdown-city", "value"),
    Input("dropdown-country", "value"),
)
def filter_city(country):
    """Callback to display only the cities that belong to the country that
    was previously selected.

    Input:
      - cou: contry value.

    Output:
      - option (list): cities list.
      - value (string): a city to display in the box.
    """

    options = [{"label": city, "value": city} for city in cities_by_country[country]]
    return options, options[0]["value"]


@callback(
    Output("global-store-bbox-latlon", "data", allow_duplicate=True),
    Output("global-store-bbox-latlon-orig", "data"),
    Output("global-store-uc-latlon", "data"),
    Output("global-store-fua-latlon", "data"),
    Output("global-store-hash", "data", allow_duplicate=True),
    Output("global-map", "viewport"),
    Output("global-polygon", "bounds"),
    Input("btn-country-select", "n_clicks"),
    State("dropdown-country", "value"),
    State("dropdown-city", "value"),
    prevent_initial_call=True,
)
def set_city(n_clicks, country, city):
    """Sets updates nav links and header.

    State:
    (A state would save the colected data but it won't trigger anything)
        - value (dropdown-country): contry value.
        - value (dropdown-city): city value.

    Input:
        - n_clicks: a click triggers the callback.

    Output:
        - children (header): a list containing the city and country in html
          format.
        - g_link: Link for historic growth page.
        - lc_link: Link for land cover.
        - sleuth_link: Link for slueth page.
    """

    if n_clicks is None or n_clicks == 0:
        return (dash.no_update,) * 7

    bbox_latlon, uc_latlon, fua_latlon = ru.get_bboxes(city, country, PATH_FUA)

    bbox_latlon_json = geometry_to_json(bbox_latlon)
    uc_latlon_json = geometry_to_json(uc_latlon)
    fua_latlon_json = geometry_to_json(fua_latlon)

    id_hash = hash_geometry(bbox_latlon_json)

    path_cache = Path(f"./data/cache/{str(id_hash)}")
    path_cache.mkdir(exist_ok=True, parents=True)

    centroid = bbox_latlon.centroid

    coords = bbox_latlon.exterior.coords
    bounds = [coords[0], coords[2]]
    bounds = [[y, x] for x, y in bounds]

    return (
        bbox_latlon_json,
        bbox_latlon_json,
        uc_latlon_json,
        fua_latlon_json,
        id_hash,
        dict(center=[centroid.y, centroid.x], transition="flyTo", zoom=9),
        bounds,
    )


@callback(
    Output("global-store-bbox-latlon", "data"),
    Output("global-store-hash", "data"),
    Output("global-custom-region-alert", "children"),
    Output("global-custom-region-alert", "is_open"),
    Output("global-custom-region-alert", "color"),
    Input("global-btn-apply-region", "n_clicks"),
    State("global-edit-control", "geojson"),
    State("global-store-bbox-latlon-orig", "data"),
    prevent_initial_call=True,
)
def set_custom_bbox(n_clicks, geojson, bbox_orig):
    if n_clicks is None or n_clicks == 0:
        return [dash.no_update] * 5

    features = geojson["features"]
    if len(features) == 0:
        id_hash = hash_geometry(bbox_orig)
        path_cache = Path(f"./data/cache/{str(id_hash)}")
        path_cache.mkdir(exist_ok=True, parents=True)
        return (
            bbox_orig,
            id_hash,
            "No se proveyó ninguna región personalizada. Se utilizará la original.",
            True,
            "warning",
        )

    bbox_json = features[0]["geometry"]
    bbox = shape(bbox_json)
    bbox_orig = shape(bbox_orig)

    if not bbox_orig.contains(bbox):
        return (
            dash.no_update,
            dash.no_update,
            "La región personalizada provista no está contenida en la original.",
            True,
            "danger",
        )

    id_hash = hash_geometry(bbox_json)
    path_cache = Path(f"./data/cache/{str(id_hash)}")
    path_cache.mkdir(exist_ok=True, parents=True)

    if len(features) == 1:
        return bbox_json, id_hash, dash.no_update, dash.no_update, dash.no_update
    else:
        return (
            bbox_json,
            id_hash,
            "Más de una región personalizada provista. Se tomará una al azar.",
            True,
            "warning",
        )