import dash
import dateutil.parser
import ee

import dash_bootstrap_components as dbc
import ursa.dynamic_world as udw

from components.page import new_page_layout
from components.text import figureWithDescription, figureWithDescription_translation
from dash import html, dcc, callback, Input, Output, State
from datetime import datetime, timezone
from layouts.common import generate_drive_text, generate_drive_text_translation
from pathlib import Path
from shapely.geometry import shape

translations = {
    "ADDITIONAL_TEXT_PART1": {
        "es": "En esta pestaña podrás explorar los tipos de cobertura de suelo presentes en el área alrededor de tu ciudad. Estos datos de cobertura de suelo provienen del proyecto",
        "en": "In this tab, you can explore the types of land cover present in the area around your city. These land cover data come from the project",
        "pt": "Nesta aba, você pode explorar os tipos de cobertura do solo presentes na área ao redor da sua cidade. Esses dados de cobertura do solo vêm do projeto"
    },
    
    "ADDITIONAL_TEXT_PART2": {
        "es": " de Google.",
        "en": " from Google.",
        "pt": " do Google."
    },
    
    "ADDITIONAL_TEXT_PART3": {
        "es": "En Dynamic World, las imágenes satelitales Sentinel son procesadas usando una red neuronal para clasificar cada pixel en una de las 9 posibles categorías de suelo. Dynamic World posee datos de cobertura de suelo desde el año 2016.",
        "en": "In Dynamic World, Sentinel satellite images are processed using a neural network to classify each pixel into one of 9 possible soil categories. Dynamic World has land cover data since 2016.",
        "pt": "Em Dynamic World, as imagens de satélite Sentinel são processadas usando uma rede neural para classificar cada pixel em uma das 9 possíveis categorias de solo. Dynamic World possui dados de cobertura do solo desde 2016."
    },
    
    "ADDITIONAL_TEXT_PART4": {
        "es": "Las correspondencias y colores canónicos de cada etiqueta pueden revisarse en el siguiente",
        "en": "The correspondences and canonical colors of each label can be reviewed in the following",
        "pt": "As correspondências e cores canônicas de cada etiqueta podem ser revisadas no seguinte"
    },
    
    "tipo-agua": {
        "es": "0: Agua",
        "en": "0: Water",
        "pt": "0: Água"
    },
    "tipo-arboles": {
        "es": "1: Árboles",
        "en": "1: Trees",
        "pt": "1: Árvores"
    },
    "tipo-pasto": {
        "es": "2: Pasto",
        "en": "2: Grass",
        "pt": "2: Grama"
    },
    "tipo-vegetacion": {
        "es": "3: Vegetación inundada",
        "en": "3: Flooded Vegetation",
        "pt": "3: Vegetação Inundada"
    },
    "tipo-cultivos": {
        "es": "4: Cultivos",
        "en": "4: Crops",
        "pt": "4: Culturas"
    },
    "tipo-arbustos": {
        "es": "5: Arbustos y maleza",
        "en": "5: Shrubs and Underbrush",
        "pt": "5: Arbustos e Sub-bosque"
    },
    "tipo-construido": {
        "es": "6: Construido",
        "en": "6: Built-up",
        "pt": "6: Construído"
    },
    "tipo-baldio": {
        "es": "7: Baldío",
        "en": "7: Barren",
        "pt": "7: Baldio"
    },
    "tipo-nieve": {
        "es": "8: Nieve y hielo",
        "en": "8: Snow and Ice",
        "pt": "8: Neve e Gelo"
    },
    
    "DESC1": {
        "es": "El gráfico de barras muestra las superficie en kilómetros cuadrados que le corresponde a cada clase de cobertura en el año 2022.",
        "en": "The bar chart shows the surface area in square kilometers corresponding to each land cover class in the year 2022.",
        "pt": "O gráfico de barras mostra a superfície em quilômetros quadrados correspondente a cada classe de cobertura do solo no ano de 2022."
    },
    
    "TITLE1": {
        "es": "Superficie por Categoría de Uso de Suelo (Año 2022)",
        "en": "Surface Area by Land Use Category (Year 2022)",
        "pt": "Superfície por Categoria de Uso do Solo (Ano 2022)"
    },
    "DESC2": {
        "es": "El gráfico de líneas muestra la evolución en el tiempo de la cantidad de superficie de cada clase de cobertura desde 2016 hasta el 2022. El gráfico es interactivo y se pueden seleccionar una o varias clases específicas para observar más claramente su comportamiento en el tiempo.",
        "en": "The line chart shows the time evolution of the surface area for each land cover class from 2016 to 2022. The chart is interactive, and one or several specific classes can be selected to more clearly observe their behavior over time.",
        "pt": "O gráfico de linhas mostra a evolução temporal da superfície de cada classe de cobertura do solo de 2016 até 2022. O gráfico é interativo, e uma ou várias classes específicas podem ser selecionadas para observar mais claramente o seu comportamento ao longo do tempo."
    },
    "TITLE2": {
        "es": "Cobertura de suelo",
        "en": "Land Cover",
        "pt": "Cobertura do Solo"
    },
    
    "TITLE3": {
        "es": "Clasificación del Territorio por Categoría de Uso de Suelo (Año 2022)",
        "en": "Land Classification by Land Use Category (Year 2022)",
        "pt": "Classificação do Território por Categoria de Uso do Solo (Ano 2022)"
    },
    
    "MAIN_TEXT": {
        "es": "El mapa muestra la categoría más común observada en 2022 para cada pixel de 10x10 metros. El relieve refleja la certeza del proceso de clasificación, una mayor altura refleja una mayor certidumbre de que el pixel pertenezca a la clase mostrada. Notese que los bordes entre clases presentan mayor incertidumbre.",
        "en": "The map displays the most common category observed in 2022 for each 10x10 meter pixel. The relief reflects the certainty of the classification process, where greater height indicates a higher certainty that the pixel belongs to the displayed class. Note that the borders between classes show greater uncertainty.",
        "pt": "O mapa exibe a categoria mais comum observada em 2022 para cada pixel de 10x10 metros. O relevo reflete a certeza do processo de classificação, onde uma maior altura indica uma maior certeza de que o pixel pertence à classe exibida. Note que as bordas entre as classes mostram maior incerteza."
    },
    
    "HOW": {
        "es": "La información procesada en la sección Cobertura de Suelo se realiza principalmente mediante de Google Earth Engine. De esta manera, la descarga de los datos empleados, debido a su tamaño, es a través del Google Drive de la cuenta empleada en la autenticación de Google Earth Engine.",
        "en": "The information processed in the Soil Coverage section is primarily done through Google Earth Engine. Therefore, the download of the used data, due to its size, is through the Google Drive of the account used in the authentication of Google Earth Engine.",
        "pt": "As informações processadas na seção Cobertura do Solo são realizadas principalmente através do Google Earth Engine. Assim, o download dos dados utilizados, devido ao seu tamanho, é feito através do Google Drive da conta utilizada na autenticação do Google Earth Engine."
    },
    "WHERE": {
        "es": "La descarga del raster con nombre 'dynamic_world_raster.tif' se hará al directorio raíz del Google Drive de la cuenta empleada.",
        "en": "The download of the raster named 'dynamic_world_raster.tif' will be made to the root directory of the Google Drive of the account used.",
        "pt": "O download do raster com o nome 'dynamic_world_raster.tif' será feito para o diretório raiz do Google Drive da conta utilizada."
    },
    
    "generate-drive-text1": {
        "es": "Descarga de Datos",
        "en": "Data Download",
        "pt": "Download de Dados"
    },
    "generate-drive-text2": {
        "es": "¿Cómo se realiza la descarga?",
        "en": "How is the download done?",
        "pt": "Como é feito o download?"
    },
    "generate-drive-text3": {
        "es": "¿Dónde se descarga el archivo?",
        "en": "Where is the file downloaded?",
        "pt": "Onde o arquivo é baixado?"
    },
    "generate-drive-text4": {
        "es": "¿Cuáles son los estados de la descarga?",
        "en": "What are the download states?",
        "pt": "Quais são os estados do download?"
    },
    "generate-drive-text5": {
        "es": "Los estados de la tarea de descarga son los siguientes:",
        "en": "The download task states are as follows:",
        "pt": "Os estados da tarefa de download são os seguintes:"
    },
    "generate-drive-text6": {
        "es": " - Pendiente en el cliente.",
        "en": " - Pending on the client.",
        "pt": " - Pendente no cliente."
    },
    "generate-drive-text7": {
        "es": " - En cola en el servidor.",
        "en": " - Queued on the server.",
        "pt": " - Em fila no servidor."
    },
    "generate-drive-text8": {
        "es": " - En ejecución.",
        "en": " - In execution.",
        "pt": " - Em execução."
    },
    "generate-drive-text9": {
        "es": " - Completada exitosamente.",
        "en": " - Completed successfully.",
        "pt": " - Completado com sucesso."
    },
    "generate-drive-text10": {
        "es": " - No completada debido a un error.",
        "en": " - Not completed due to an error.",
        "pt": " - Não concluído devido a um erro."
    },
    "generate-drive-text11": {
        "es": " - En ejecución pero se ha solicitado su cancelación.",
        "en": " - In execution but its cancellation has been requested.",
        "pt": " - Em execução, mas seu cancelamento foi solicitado."
    },
    "generate-drive-text12": {
        "es": " - Cancelada.",
        "en": " - Cancelled.",
        "pt": " - Cancelado."
    },
    "generate-drive-text13": {
        "es": "¿Es posible hacer descargas simultáneas?",
        "en": "Is it possible to make simultaneous downloads?",
        "pt": "É possível fazer downloads simultâneos?"
    },
    "generate-drive-text14": {
        "es": "URSA únicamente permite la ejecución de una tarea de descarga a la vez. Espere a que se complete la tarea antes de crear una nueva. Esto puede tomar varios minutos.",
        "en": "URSA only allows the execution of one download task at a time. Wait for the task to complete before creating a new one. This may take several minutes.",
        "pt": "URSA só permite a execução de uma tarefa de download por vez. Aguarde a conclusão da tarefa antes de criar uma nova. Isso pode levar vários minutos."
    },
    
    "lc-btn-download-rasters": {
        "es": "Descarga rasters",
        "en": "Download Rasters",
        "pt": "Baixar Rasters"
    },
   # "info-button1": {
    #    "es": "Descarga los archivos Raster a Google Drive. En este caso la información es procesada en Google Earth Engine y la única opción de descarga es al directorio raíz de tu Google Drive.",
     #   "en": "Download Raster files to Google Drive. In this case, the information is processed in Google Earth Engine, and the only download option is to the root directory of your Google Drive.",
      #  "pt": "Baixe os arquivos Raster para o Google Drive. Neste caso, as informações são processadas no Google Earth Engine, e a única opção de download é para o diretório raiz do seu Google Drive."
    #},
    "lc-btn-stop-task": {
        "es": "Cancelar ejecución",
        "en": "Cancel Execution",
        "pt": "Cancelar Execução"
    }
    
}


path_fua = Path("./data/output/cities/")

dash.register_page(
    __name__,
    title="URSA",
)

MAIN_TEXT = """El mapa muestra la categoría mas común observada en 2022
        para cada pixel de 10x10 metros.
        El relieve refleja la certeza del proceso de clasificación,
        una mayor altura refleja una mayor certidumbre de que el
        pixel pertnezca a la clase mostrada.
        Notese que los bordes entre clases presentan mayor
        incertidumbre. """

ADDITIONAL_TEXT = [
    html.Div(id='ADDITIONAL_TEXT_PART1'),
    html.A("Dynamic World", href="https://dynamicworld.app"),
    html.Div(id='ADDITIONAL_TEXT_PART2'),
    html.Br(),
    html.Div(id='ADDITIONAL_TEXT_PART3'),
    html.Br(),
    html.Div(id='ADDITIONAL_TEXT_PART4'),
    html.A(
        "enlace",
        href="https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1#bands",
    ),
    ":",
    html.Ul(
        [
            html.Li(id = "tipo-agua"),
            html.Li(id = "tipo-arboles"),
            html.Li(id = "tipo-pasto"),
            html.Li(id = "tipo-vegetacion"),
            html.Li(id = "tipo-cultivos"),
            html.Li(id = "tipo-arbustos"),
            html.Li(id = "tipo-construido"),
            html.Li(id = "tipo-baldio"),
            html.Li(id = "tipo-nieve"),
        ]
    ),
]

maps = html.Div(
    [
        dcc.Graph(style={"height": "100%"}, id="cover-map-1"),
    ],
    style={"height": "100%"},
)

lines = html.Div(
    [
        figureWithDescription_translation(
        dcc.Graph(id="cover-lines-1"),
        "DESC1",  # ID descripción
        "TITLE1"  # ID título
        ),
        
        figureWithDescription_translation(
        dcc.Graph(id="cover-lines-2"),
        "DESC2",  # ID descripción
        "TITLE2"  # ID título
        ),
    ],
    style={"overflow": "scroll", "height": "82vh"},
)

main_info = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id="TITLE3"), 
            html.Div(id="MAIN_TEXT"),  
        ]
    ),
    class_name="main-info",
)

additional_info = dbc.Card(dbc.CardBody(ADDITIONAL_TEXT), class_name="supp-info")

tabs = [
    dbc.Tab(
        lines,
        label="Gráficas",
        id="tab-plots",
        tab_id="tabPlots",
    ),
    dbc.Tab(
        html.Div([main_info, additional_info]),
        label="Info",
        id="tab-info",
        tab_id="tabInfo",
    ),
    dbc.Tab(
        [
            generate_drive_text_translation(
                how="La información procesada en la sección Cobertura de Suelo se realiza principalmente mediante de Google Earth Engine. De esta manera, la descarga de los datos empleados, debido a su tamaño, es a través del Google Drive de la cuenta empleada en la autenticación de Google Earth Engine.",
                where="La descarga del raster con nombre 'dynamic_world_raster.tif' se hará al directorio raíz del Google Drive de la cuenta empleada.",
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    html.Span(id = "info-button1"),
                                    #"Descarga rasters",
                                    id="lc-btn-download-rasters",
                                    color="light",
                                    title="Descarga los archivos Raster a Google Drive. En este caso la información es procesada en Google Earth Engine y la única opción de descarga es al directorio raíz de tu Google Drive.",
                                    #html.Span(id = "info-button1"),
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    #"Cancelar ejecución",
                                    id="lc-btn-stop-task",
                                    color="danger",
                                    style={"display": "none"},
                                ),
                                width=4,
                            ),
                        ],
                        justify="center",
                    ),
                    dbc.Row(
                        dbc.Col(html.Span(id="lc-span-rasters-output"), width=3),
                        justify="center",
                    ),
                ],
            ),
        ],
        label="Descargables",
    ),
]

# Traducciones
language_buttons = dbc.ButtonGroup(
    [
        dbc.Button("Español", id="btn-lang-es", n_clicks=0),
        dbc.Button("English", id="btn-lang-en", n_clicks=0),
        dbc.Button("Portuguese", id="btn-lang-pt", n_clicks=0),
    ],
    style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1"},
)

layout = new_page_layout(
    maps,
    tabs,
    stores=[
        dcc.Store(id="lc-store-task-name"),
        dcc.Interval(id="lc-interval", interval=10000, n_intervals=0, disabled=True),
        dcc.Location(id="lc-location"),
    ],
)

layout = html.Div(
    [language_buttons, layout],
    style={"position": "relative"}
)

@callback(
    [Output(key, 'children') for key in translations.keys()],
    [Input('btn-lang-es', 'n_clicks'),
     Input('btn-lang-en', 'n_clicks'),
     Input('btn-lang-pt', 'n_clicks')]
)
def update_translated_content(btn_lang_es, btn_lang_en, btn_lang_pt):
    ctx = dash.callback_context

    if not ctx.triggered:
        language = 'es'  # Predeterminado
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        language = 'es' if button_id == 'btn-lang-es' else 'en' if button_id == 'btn-lang-en' else 'pt'

    return [translations[key][language] for key in translations.keys()]

# ---


@callback(
    Output("lc-interval", "disabled", allow_duplicate=True),
    Output("lc-store-task-name", "data"),
    Output("lc-btn-stop-task", "style", allow_duplicate=True),
    Output("lc-span-rasters-output", "children", allow_duplicate=True),
    Input("lc-btn-download-rasters", "n_clicks"),
    State("global-store-bbox-latlon", "data"),
    State("lc-store-task-name", "data"),
    prevent_initial_call=True,
)
def start_download(n_clicks, bbox_latlon, task_name):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update, dash.no_update, dash.no_update

    if task_name is None:
        bbox_latlon = shape(bbox_latlon)
        task = udw.download_map_season(bbox_latlon, "Qall", 2022)
        status = task.status()
        return False, status["name"], {"display": "block"}, "Iniciando descarga"
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output("lc-span-rasters-output", "children", allow_duplicate=True),
    Output("lc-interval", "disabled", allow_duplicate=True),
    Input("lc-interval", "n_intervals"),
    State("lc-store-task-name", "data"),
    prevent_initial_call=True,
)
def download_rasters(n_intervals, task_name):
    task_metadata = ee.data.getOperation(task_name)["metadata"]
    state = task_metadata["state"]

    start_time = task_metadata["createTime"]
    start_time = dateutil.parser.isoparse(start_time)

    current_time = datetime.now(timezone.utc)
    time_elapsed = (current_time - start_time).total_seconds()

    if state in ("COMPLETED", "FAILED", "CANCELLED", "SUCCEEDED"):
        return [f"Status de la Descarga: {state}, Tiempo transcurrido: {int(time_elapsed)} segundos"], True

    return [f"Status de la Descarga: {state}, Tiempo transcurrido: {int(time_elapsed)} segundos"], False
    


@callback(
    Output("cover-map-1", "figure"),
    Output("cover-lines-1", "figure"),
    Output("cover-lines-2", "figure"),
    Output("lc-location", "pathname"),
    Input("global-store-hash", "data"),
    Input("global-store-bbox-latlon", "data"),
    Input("global-store-fua-latlon", "data"),
)
def generate_plots(id_hash, bbox_latlon, fua_latlon):
    if id_hash is None:
        return [dash.no_update] * 3 + ["/"]

    path_cache = Path(f"./data/cache/{id_hash}")

    bbox_latlon = shape(bbox_latlon)
    fua_latlon = shape(fua_latlon)

    map1 = udw.plot_map_season(
        bbox_latlon, fua_latlon.centroid, season="Qall", year=2022
    )
    lines1 = udw.plot_lc_year(bbox_latlon, path_cache)
    lines2 = udw.plot_lc_time_series(bbox_latlon, path_cache)

    return map1, lines1, lines2, dash.no_update


@callback(
    Output("lc-btn-stop-task", "style"),
    Output("lc-interval", "disabled"),
    Output("lc-span-rasters-output", "children"),
    Input("lc-btn-stop-task", "n_clicks"),
    State("lc-store-task-name", "data"),
    prevent_initial_call=True,
)
def stop_task(n_clicks, task_id):
    ee.data.cancelOperation(task_id)
    return {"display": "none"}, True, "Descarga cancelada"