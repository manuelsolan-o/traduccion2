import dash
import dateutil
import ee

import dash_bootstrap_components as dbc
import pandas as pd
import ursa.heat_islands as ht
import ursa.plots.heat_islands as pht
import ursa.utils.date as du
import ursa.utils.geometry as ug
import ursa.utils.raster as ru
import ursa.world_cover as wc

from components.text import figureWithDescription, figureWithDescription_translation, figureWithDescription_translation2
from components.page import new_page_layout
from dash import html, dcc, callback, Input, Output, State
from datetime import datetime, timezone
from layouts.common import generate_drive_text, generate_drive_text_translation
from pathlib import Path
from shapely.geometry import shape


translations = {
    "HISTOGRAM_TEXT": {
        "es": "Este diagrama de barras muestra la superficie en kilómetros cuadrados del suelo que forma parte del área de análisis para cada una de las 7 categorías de temperatura, para el suelo tanto rural como urbano. Las categorías de temperatura se particionan de la siguiente forma:",
        "en": "This bar chart shows the surface area in square kilometers of the land that is part of the analysis area for each of the 7 temperature categories, for both rural and urban soil. The temperature categories are partitioned as follows:",
        "pt": "Este diagrama de barras mostra a superfície em quilômetros quadrados do solo que faz parte da área de análise para cada uma das 7 categorias de temperatura, tanto para o solo rural quanto urbano. As categorias de temperatura são divididas da seguinte forma:"
    },
    
    "categoria-muy-frio": {
        "es": "Muy frío: < -2.5σ",
        "en": "Very Cold: < -2.5σ",
        "pt": "Muito Frio: < -2.5σ"
    },
    "categoria-frio": {
        "es": "Frío: ≥ -2.5σ, < -1.5σ",
        "en": "Cold: ≥ -2.5σ, < -1.5σ",
        "pt": "Frio: ≥ -2.5σ, < -1.5σ"
    },
    "categoria-ligeramente-frio": {
        "es": "Ligeramente frío: ≥ -1.5σ, < -0.5σ",
        "en": "Slightly Cold: ≥ -1.5σ, < -0.5σ",
        "pt": "Ligeiramente Frio: ≥ -1.5σ, < -0.5σ"
    },
    "categoria-templado": {
        "es": "Templado: ≥ -0.5σ, < 0.5σ",
        "en": "Temperate: ≥ -0.5σ, < 0.5σ",
        "pt": "Temperado: ≥ -0.5σ, < 0.5σ"
    },
    "categoria-ligeramente-calido": {
        "es": "Ligeramente cálido: ≥ 0.5σ, < 1.5σ",
        "en": "Slightly Warm: ≥ 0.5σ, < 1.5σ",
        "pt": "Ligeiramente Quente: ≥ 0.5σ, < 1.5σ"
    },
    "categoria-caliente": {
        "es": "Caliente: ≥ 1.5σ, < 2.5σ",
        "en": "Hot: ≥ 1.5σ, < 2.5σ",
        "pt": "Quente: ≥ 1.5σ, < 2.5σ"
    },
    "categoria-muy-caliente": {
        "es": "Muy caliente: ≥ 2.5σ",
        "en": "Very Hot: ≥ 2.5σ",
        "pt": "Muito Quente: ≥ 2.5σ"
    },
    "desviacion": {
        "es": "σ: desviación estándar",
        "en": "σ: standard deviation",
        "pt": "σ: desvio padrão"
    },
    
    "impactView1": {
        "es": "Impacto",
        "en": "Impact",
        "pt": "Impacto"
    },
    "impactView2": {
        "es": "Nueva temperatura promedio",
        "en": "New Average Temperature",
        "pt": "Nova Temperatura Média"
    },
    "impactView3": {
        "es": "Promedio mitigados",
        "en": "Average Mitigated",
        "pt": "Média Mitigada"
    },
    "impactView4": {
        "es": "Área urbana intervenida",
        "en": "Urban Area Intervened",
        "pt": "Área Urbana Intervencionada"
    },
    "impactView5": {
        "es": "Caminos intervenidos",
        "en": "Paths Intervened",
        "pt": "Caminhos Intervencionados"
    },
    
    "strategyList1": {
        "es": "Estrategias de mitigación",
        "en": "Mitigation Strategies",
        "pt": "Estratégias de Mitigação"
    },
    "strategyList2": {
        "es": "Selecciona las estrategias a implementar. Puedes encontrar más información de cada estrategia o seleccionar múltiples.",
        "en": "Select the strategies to implement. You can find more information on each strategy or select multiple.",
        "pt": "Selecione as estratégias a implementar. Você pode encontrar mais informações sobre cada estratégia ou selecionar várias."
    },
    
    "MAP_INTRO_TEXT": {
        "es": "El mapa a continuación muestra la desviación de temperatura de cada píxel en la superficie construida de la ciudad con respecto a la temperatura rural con un código de colores en 7 categorías. El color rojo más oscuro corresponde a las zonas urbana con una temperatura registrada que tiene la mayor desviación respecto a la temperatura rural en la zona circundante a la zona de interés (más de 2.5 desviaciones estándar de la media rural). Estas zonas en un color más oscuro corresponden a las islas de calor en la ciudad. Esta metodología que compara las temperaturas rurales y urbanas en una misma región es la más apropiada y generalizable, ya que al restar la temperatura media rural a la de cada píxel, se remueven variaciones locales y se puede comparar la intensidad de las islas de calor de ciudades en distintas latitudes.",
        "en": "The map below shows the temperature deviation of each pixel in the city's built surface relative to the rural temperature with a color code in 7 categories. The darkest red color corresponds to urban areas with a recorded temperature that has the greatest deviation from the rural temperature in the area surrounding the zone of interest (more than 2.5 standard deviations from the rural average). These darker colored areas correspond to the heat islands in the city. This methodology, which compares rural and urban temperatures in the same region, is the most appropriate and generalizable, as subtracting the average rural temperature from each pixel removes local variations and allows for comparison of the intensity of heat islands in cities at different latitudes.",
        "pt": "O mapa abaixo mostra o desvio de temperatura de cada pixel na superfície construída da cidade em relação à temperatura rural com um código de cores em 7 categorias. A cor vermelha mais escura corresponde às áreas urbanas com uma temperatura registrada que tem o maior desvio em relação à temperatura rural na área circundante à zona de interesse (mais de 2,5 desvios padrão da média rural). Essas áreas de cor mais escura correspondem às ilhas de calor na cidade. Esta metodologia, que compara temperaturas rurais e urbanas na mesma região, é a mais apropriada e generalizável, pois ao subtrair a temperatura média rural de cada pixel, remove-se variações locais e permite comparar a intensidade das ilhas de calor em cidades de diferentes latitudes."
    },
    
    "title1": {
        "es": "Frecuencia de la superficie (Km²) de análisis por categoría de temperatura",
        "en": "Frequency of Analysis Surface Area (Km²) by Temperature Category",
        "pt": "Frequência da Superfície (Km²) de Análise por Categoria de Temperatura"
    },
    
    "BARS_TEXT" : {
    "es": "Las barras verticales en este gráfico suman 1 (o 100%) cada una. Las barras desglosan la composición de la superficie por tipo de uso de suelo para cada una de las 7 categorías de temperatura. Se puede apreciar que las temperaturas más frías se asocian con superficie de manglares o coberturas verdes, mientras que las superficies más calientes se componen principalmente de suelo construido y praderas.",
    "en": "The vertical bars in this chart sum to 1 (or 100%) each. The bars break down the surface composition by land use type for each of the 7 temperature categories. It can be seen that the colder temperatures are associated with mangrove surface or green coverings, while the hotter surfaces are mainly composed of built soil and grasslands.",
    "pt": "As barras verticais neste gráfico somam 1 (ou 100%) cada uma. As barras detalham a composição da superfície por tipo de uso do solo para cada uma das 7 categorias de temperatura. Pode-se observar que as temperaturas mais frias estão associadas à superfície de manguezais ou coberturas verdes, enquanto as superfícies mais quentes são compostas principalmente por solo construído e pastagens."
    },
    
    "title2": {
        "es": "Fracción de uso de suelo por categoría de temperatura",
        "en": "Land Use Fraction by Temperature Category",
        "pt": "Fração de Uso do Solo por Categoria de Temperatura"
    },
    
    "title3": {
        "es": "Temperatura en función de la distancia al centro urbano",
        "en": "Temperature in Relation to Distance from Urban Center",
        "pt": "Temperatura em Função da Distância ao Centro Urbano"
    },
    
    "empty-desc1":{
        "es": "",
        "en": "",
        "pt": ""
    },
    
    "title4": {
        "es": "Fracción de uso de suelo en función de la distancia al centro urbano",
        "en": "Land Use Fraction in Relation to Distance from Urban Center",
        "pt": "Fração de Uso do Solo em Função da Distância ao Centro Urbano"
    },
    
    "empty-desc2":{
        "es": "",
        "en": "",
        "pt": ""
    },
    
    "WELCOME_CONTENT_PART1": {
        "es": "Este apartado muestra un análisis sobre ",
        "en": "This section displays an analysis on ",
        "pt": "Esta seção mostra uma análise sobre "
    },
    "WELCOME_CONTENT_PART2": {
        "es": "islas de calor",
        "en": "heat islands",
        "pt": "ilhas de calor"
    },
    "WELCOME_CONTENT_PART3": {
        "es": " y el potencial impacto de estrategias de mitigación. La ",
        "en": " and the potential impact of mitigation strategies. The ",
        "pt": " e o potencial impacto de estratégias de mitigação. A "
    },
    "WELCOME_CONTENT_PART4": {
        "es": "metodología",
        "en": "methodology",
        "pt": "metodologia"
    },
    "WELCOME_CONTENT_PART5": {
        "es": " (Zhou et al., 2018) para identificar islas de calor consiste en contrastar la temperatura promedio anual de un píxel urbano (100x100 metros) contra la temperatura promedio anual de los píxeles rurales en la misma zona geográfica de la ciudad. Cada píxel de la zona de interés se clasifica en rural o urbano, utilizando el conjunto de datos WorldCover de la Agencia Espacial Europea (ESA).",
        "en": " (Zhou et al., 2018) for identifying heat islands involves contrasting the annual average temperature of an urban pixel (100x100 meters) against the annual average temperature of rural pixels in the same geographical area of the city. Each pixel in the area of interest is classified as rural or urban, using the WorldCover dataset from the European Space Agency (ESA).",
        "pt": " (Zhou et al., 2018) para identificar ilhas de calor envolve contrastar a temperatura média anual de um pixel urbano (100x100 metros) contra a temperatura média anual dos pixels rurais na mesma área geográfica da cidade. Cada pixel na área de interesse é classificado como rural ou urbano, utilizando o conjunto de dados WorldCover da Agência Espacial Europeia (ESA)."
    },
    
    "temperature": {
        "es": "Temperatura promedio",
        "en": "Average Temperature",
        "pt": "Temperatura Média"
    },
    
    "satellite_image_data": {
        "es": "* Datos obtenidos para el año 2022 a partir de la imagen satelital",
        "en": "* Data obtained for the year 2022 from the satellite image",
        "pt": "* Dados obtidos para o ano de 2022 a partir da imagem de satélite"
    },
    
    "suhi-btn-download-rasters": {
        "es": "Descargar rasters",
        "en": "Download Rasters",
        "pt": "Baixar Rasters"
    },
    "suhi-btn-stop-task": {
        "es": "Cancelar ejecución",
        "en": "Cancel Execution",
        "pt": "Cancelar Execução"
    },
    "suhi-btn-download-csv": {
        "es": "Descargar CSV",
        "en": "Download CSV",
        "pt": "Baixar CSV"
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
    
    "HOW": {
        "es": "La información procesada en la sección Islas de Calor se realiza incluyendo Google Earth Engine. De esta manera, la descarga de los datos empleados, debido a su tamaño, es a través del Google Drive de la cuenta empleada en la autenticación de Google Earth Engine en el caso del raster y al disco local en el caso de los datos tabulares para hacer la visualizaciones.",
        "en": "The information processed in the Heat Islands section is carried out including Google Earth Engine. Thus, the download of the data used, due to its size, is through the Google Drive of the account used in the authentication of Google Earth Engine for raster data, and to the local disk for tabular data for visualizations.",
        "pt": "As informações processadas na seção Ilhas de Calor são realizadas incluindo o Google Earth Engine. Assim, o download dos dados utilizados, devido ao seu tamanho, é feito através do Google Drive da conta usada na autenticação do Google Earth Engine para dados raster, e para o disco local para dados tabulares para visualizações."
    },
    "WHERE": {
        "es": "La descarga del raster con nombre 'suhi_raster.tif' se hará al directorio raíz del Google Drive de la cuenta empleada. Por otro lado, el archivo descargado a disco es 'city-country-suhi-data.csv', reemplazando 'city' por la ciudad y 'country' por el país analizado, respectivamente.",
        "en": "The download of the raster named 'suhi_raster.tif' will be made to the root directory of the Google Drive of the account used. On the other hand, the file downloaded to disk is 'city-country-suhi-data.csv', replacing 'city' with the city and 'country' with the analyzed country, respectively.",
        "pt": "O download do raster chamado 'suhi_raster.tif' será feito para o diretório raiz do Google Drive da conta utilizada. Por outro lado, o arquivo baixado para o disco é 'city-country-suhi-data.csv', substituindo 'city' pela cidade e 'country' pelo país analisado, respectivamente."
    },
    
    # STRATEGIES
    
    "strat-vegetacion-title": {
        "es": "Reintroducción de vegetación",
        "en": "Reintroduction of Vegetation",
        "pt": "Reintrodução de Vegetação"
    },
    
    "strat-vegetacion-desc": {
        "es": "Reintroducir vegetación a al menos 16% del área urbana a través de parques, jardines y camellones puede generar un enfriamiento de 1.07 °C promedio.",
        "en": "Reintroducing vegetation to at least 16% of the urban area through parks, gardens, and road medians can generate an average cooling of 1.07 °C.",
        "pt": "Reintroduzir vegetação em pelo menos 16% da área urbana através de parques, jardins e canteiros centrais pode gerar um resfriamento médio de 1.07 °C."
    },
    
    "strat-techos-verdes-title": {
        "es": "Instalación de techos verdes",
        "en": "Installation of Green Roofs",
        "pt": "Instalação de Telhados Verdes"
    },
    
    "strat-techos-verdes-desc": {
        "es": "Instalar techos verdes en 50% de la superficie de techo disponible reduce un promedio de 0.083°C",
        "en": "Installing green roofs on 50% of the available roof surface reduces an average of 0.083°C",
        "pt": "Instalar telhados verdes em 50% da superfície do telhado disponível reduz em média 0.083°C"
    },
    
    "strat-techos-frescos-title": {
        "es": "Instalación de techos frescos",
        "en": "Installation of Cool Roofs",
        "pt": "Instalação de Telhados Frescos"
    },
    
    "strat-techos-frescos-desc": {
        "es": "Incrementar el albedo a 0.5 en el 50% de los techos de la ciudad por medio de materiales reflectores en los techos reduce la temperatura un promedio de 0.078°C",
        "en": "Increasing the albedo to 0.5 on 50% of the city's roofs using reflective materials on the roofs reduces the temperature by an average of 0.078°C",
        "pt": "Aumentar o albedo para 0.5 em 50% dos telhados da cidade por meio de materiais refletores nos telhados reduz a temperatura em média 0.078°C"
    },
    
    "strat-pavimento-concreto-title": {
        "es": "Instalación de pavimentos de concreto",
        "en": "Installation of Concrete Pavements",
        "pt": "Instalação de Pavimentos de Concreto"
    },
    
    "strat-pavimento-concreto-desc": {
        "es": "Cambiar los pavimentos de asfalto por pavimentos de concreto tiene la capacidad de reducir un promedio de 0.39ºC.",
        "en": "Changing asphalt pavements to concrete pavements has the ability to reduce an average of 0.39ºC.",
        "pt": "Mudar os pavimentos de asfalto para pavimentos de concreto tem a capacidade de reduzir em média 0.39ºC."
    },
    
    "strat-pavimento-reflector-title": {
        "es": "Instalación de pavimentos reflectores",
        "en": "Installation of Reflective Pavements",
        "pt": "Instalação de Pavimentos Refletores"
    },
    
    "strat-pavimento-reflector-desc": {
        "es": "Incrementar el albedo en 0.2 en todos los pavimentos de la ciudad mediante materiales o pinturas reflectoras en tiene la capacidad de reducir la temperatura en 1.39 °C promedio",
        "en": "Increasing the albedo by 0.2 on all city pavements using materials or reflective paints has the ability to reduce the temperature by an average of 1.39 °C",
        "pt": "Aumentar o albedo em 0.2 em todos os pavimentos da cidade usando materiais ou tintas refletoras tem a capacidade de reduzir a temperatura em média 1.39 °C"
    },
    
    # Colores
    
    "color-muy-frio": {
        "es": "Muy frío",
        "en": "Very Cold",
        "pt": "Muito Frio"
    },
    "color-frio": {
        "es": "Frío",
        "en": "Cold",
        "pt": "Frio"
    },
    "color-ligeramente-frio": {
        "es": "Ligeramente frío",
        "en": "Slightly Cold",
        "pt": "Ligeiramente Frio"
    },
    "color-templado": {
        "es": "Templado",
        "en": "Temperate",
        "pt": "Temperado"
    },
    "color-ligeramente-calido": {
        "es": "Ligeramente cálido",
        "en": "Slightly Warm",
        "pt": "Ligeiramente Quente"
    },
    "color-caliente": {
        "es": "Caliente",
        "en": "Hot",
        "pt": "Quente"
    },
    "color-muy-caliente": {
        "es": "Muy caliente",
        "en": "Very Hot",
        "pt": "Muito Quente"
    }
}

tab_translations = {
    
    "tab-controls-suhi": {
        "es": "Controles",
        "en": "Controls",
        "pt": "Controles"
    },
    
    "tab-plots-suhi": {
        "es": "Gráficas",
        "en": "Charts",
        "pt": "Gráficos"
    },
    "tab-info-suhi": {
        "es": "Info",
        "en": "Info",
        "pt": "Informação"
    },
    "tabDownloadables-suhi": {
        "es": "Descargables",
        "en": "Downloadables",
        "pt": "Descarregáveis"
    }
}


start_time_suhi = None

SEASON = "Qall"
YEAR = 2022

path_fua = Path("./data/output/cities/")

dash.register_page(
    __name__,
    title="URSA",
)

WELCOME_CONTENT = [
    html.P(
        [
            html.Span(id="WELCOME_CONTENT_PART1"),
            html.Strong(id="WELCOME_CONTENT_PART2"),
            html.Span(id="WELCOME_CONTENT_PART3"),
            html.A(id="WELCOME_CONTENT_PART4", href="https://www.mdpi.com/2072-4292/11/1/48"),
            
            html.Span(id="WELCOME_CONTENT_PART5"),
        ]
    ),
    html.Hr(style={"width": "70%", "margin-left": "30%"}),
    html.P(
        (
            "Zhou, D., Xiao, J., Bonafoni, S., Berger, C., Deilami, K., "
            "Zhou, Y., ... & Sobrino, J. A. (2018). "
            "Satellite remote sensing of surface urban heat islands: "
            "Progress, challenges, and perspectives. Remote Sensing, "
            "11(1), 48."
        ),
        style={
            "fontStyle": "italic",
            "fontSize": "0.9rem",
            "textAlign": "right",
            "width": "70%",
            "margin-left": "30%",
        },
    ),
]


MAP_INTRO_TEXT = (
    "El mapa a continuación muestra la desviación de temperatura de cada "
    "píxel en la superficie construida de la ciudad con respecto a la "
    "temperatura rural con un código de colores en 7 categorías. "
    "El color rojo más oscuro corresponde a las zonas urbana con una "
    "temperatura registrada que tiene la mayor desviación respecto a "
    "la temperatura rural en la zona circundante a la zona de interés "
    "(más de 2.5 desviaciones estándar de la media rural). "
    "Estas zonas en un color más oscuro corresponden a las islas de "
    "calor en la ciudad. "
    "Esta metodología que compara las temperaturas rurales y urbanas "
    "en una misma región es la más apropiada y generalizable, ya que "
    "al restar la temperatura media rural a la de cada píxel, "
    "se remueven variaciones locales y se puede comparar la intensidad "
    "de las islas de calor de ciudades en distintas latitudes."
)

MAP_TEXT = (
    "La información del mapa de las islas de calor se desglosa en una "
    "serie de gráficos que comparan su incidencia contra el tipo de uso "
    "de suelo en la región."
)

HISTOGRAMA_TEXT = html.P(
    [
        html.Span(id="HISTOGRAM_TEXT"),  
        html.Ol(
            [
                html.Li(html.Span(id="categoria-muy-frio")),
                html.Li(html.Span(id="categoria-frio")),
                html.Li(html.Span(id="categoria-ligeramente-frio")),
                html.Li(html.Span(id="categoria-templado")),
                html.Li(html.Span(id="categoria-ligeramente-calido")),
                html.Li(html.Span(id="categoria-caliente")),
                html.Li(html.Span(id="categoria-muy-caliente")),
            ]
        ),
        html.Span(id="desviacion"), 
    ]
)


BARS_TEXT = (
    "Las barras verticales en este gráfico suman 1 (o 100%) cada una. "
    "Las barras desglosan la composición de la superficie por tipo de "
    "uso de suelo para cada una de las 7 categorías de temperatura. "
    "Se puede apreciar que las temperaturas más frías se asocian con "
    "superficie de manglares o coberturas verdes, "
    "mientras que las superficies más calientes se componen principalmente "
    "de suelo construido y praderas."
)

LINE_TEXT = (
    "Un aspecto interesante a considerar es la variación de la temperatura "
    "en la superficie conforme nos alejamos del centro de la ciudad. "
    "Se espera que las islas de calor disminuyan conforme nos alejamos "
    "del centro de la zona urbana, que típicamente tiene la mayor "
    "superficie construida. "
    "Para evaluar esto, generamos “donas” concéntricas con radios "
    "crecientes. Con esto, calculamos la media de la SUHII de todos los "
    "pixeles contenidos en cada dona, y la graficamos en esta imagen. "
    "El gráfico muestra el diferencial de temperatura en ese radio específico"
    "y no de forma acumulada"
    "Se puede apreciar el gradiente de disminución de la temperatura "
    "promedio conforme incrementamos el radio de las “donas”, "
    "esto es, conforme nos alejamos del centro de la zona urbana."
)

AREA_TEXT = (
    "Podemos utilizar las “donas” concéntricas del gráfico anterior "
    "para calcular el uso de suelo en cada radio conforme nos alejamos "
    "de la zona central. "
    "Típicamente, lo que ocurre es que cerca del centro de la ciudad, "
    "la gran mayoría del suelo está cubierto de suelo construido; "
    "entre más nos alejamos, más disminuye esta categoría y aumenta "
    "la fracción de cobertura verde."
    "Cabe destacar que la composición de uso de suelo en cada radio o distancia"
    "no es acumulada, sino que es específica para esa dona en particular. "
    "Finalmente, cerca de los bordes de la ciudad, podemos observar una "
    "mezcla de varias coberturas, como xsparte del proceso de urbanización."
)

MEAN_TEMPERATURE_STYLE = {"font-weight": "lighter", "font-size": "3rem"}

SUBTITLE_STYLE = {"font-size": "100"}

RESULT_STYLE = {"font-weight": "lighter"}

STRATEGIES = {
    "strat-vegetacion": {
        "title": "Reintroducción de vegetación",
        "description": (
            "Reintroducir vegetación a al menos 16% del área "
            "urbana a través de parques, jardines y camellones"
            " puede generar un enfriamiento de 1.07 °C promedio."
        ),
        "mitigation": 1.07,
        "area_fraction": 0.16,
    },
    "strat-techos-verdes": {
        "title": "Instalación de techos verdes",
        "description": (
            "Instalar techos verdes en 50% de la superficie "
            "de techo disponible reduce un promedio de 0.083°C"
        ),
        "mitigation": 0.083,
        "area_fraction": 0.5,
    },
    "strat-techos-frescos": {
        "title": "Instalación de techos frescos",
        "description": (
            "Incrementar el albedo a 0.5 en el 50% de los techos "
            "de la ciudad  por medio de materiales reflectores en "
            "los techos reduce la temperatura un promedio de "
            "0.078°C"
        ),
        "mitigation": 0.078,
        "area_fraction": 0.5,
    },
    "strat-pavimento-concreto": {
        "title": "Instalación de pavimentos de concreto",
        "description": (
            "Cambiar los pavimentos de asfalto por pavimentos "
            "de concreto tiene la capacidad de reducir un "
            "promedio de 0.39ºC."
        ),
        "mitigation": 0.39,
        "area_fraction": 1.0,
    },
    "strat-pavimento-reflector": {
        "title": "Instalación de pavimentos reflectores",
        "description": (
            "Incrementar el albedo en 0.2 en todos los "
            "pavimentos de la ciudad mediante materiales o "
            "pinturas reflectoras en tiene la capacidad de "
            "reducir la temperatura en 1.39 °C promedio"
        ),
        "mitigation": 1.39,
        "area_fraction": 1.0,
    },
}


def format_temp(temp):
    return f"{round(temp, 2)} °C"


impactView = html.Div(
    [
        html.H4(id = "impactView1", className="text-primary"),
        html.Div(id = "impactView2", style=SUBTITLE_STYLE),
        html.Div("", id="impact-result-degrees", style=RESULT_STYLE),
        html.Div(id = "impactView3", style=SUBTITLE_STYLE),
        html.Div(
            "",
            id="impact-mitigated-degrees",
            className="text-success",
            style=RESULT_STYLE,
        ),
        html.Div(id = "impactView4", style=SUBTITLE_STYLE),
        html.Div("", id="impact-result-square-kilometers", style=RESULT_STYLE),
        html.Div(id = "impactView5", style=SUBTITLE_STYLE),
        html.Div("", id="impact-result-kilometers", style=RESULT_STYLE),
    ]
)

strategyList = html.Div(
    [
        html.H4(id="strategyList1", className="text-primary"),
        html.P(html.Span(id="strategyList2")),
        html.Div(
            dcc.Checklist(
                options=[
                    {
                        "label": html.Div(
                            [
                                html.P(
                                    html.Span(id="strat-vegetacion-title"),
                                    #STRATEGIES["strat-vegetacion"]["title"],
                                    id="check-strat-vegetacion",
                                    style={"display": "inline"},
                                ),
                                dbc.Popover(
                                    dbc.PopoverBody(html.Span(id="strat-vegetacion-desc")),
                                    target="check-strat-vegetacion",
                                    trigger="hover",
                                ),
                            ],
                            style={"display": "inline"},
                        ),
                        "value": "strat-vegetacion",
                    },
                    {
                        "label": html.Div(
                            [
                                html.P(
                                    html.Span(id="strat-techos-verdes-title"),
                                    id="check-strat-techos-verdes",
                                    style={"display": "inline"},
                                ),
                                dbc.Popover(
                                    dbc.PopoverBody(html.Span(id="strat-techos-verdes-desc")),
                                    target="check-strat-techos-verdes",
                                    trigger="hover",
                                ),
                            ],
                            style={"display": "inline"},
                        ),
                        "value": "strat-techos-verdes",
                    },
                    {
                        "label": html.Div(
                            [
                                html.P(
                                    html.Span(id="strat-techos-frescos-title"),
                                    id="check-strat-techos-frescos",
                                    style={"display": "inline"},
                                ),
                                dbc.Popover(
                                    dbc.PopoverBody(html.Span(id="strat-techos-frescos-desc")),
                                    target="check-strat-techos-frescos",
                                    trigger="hover",
                                ),
                            ],
                            style={"display": "inline"},
                        ),
                        "value": "strat-techos-frescos",
                    },
                    {
                        "label": html.Div(
                            [
                                html.P(
                                    html.Span(id = "strat-pavimento-concreto-title"),
                                    id="check-strat-pavimento-concreto",
                                    style={"display": "inline"},
                                ),
                                dbc.Popover(
                                    dbc.PopoverBody(html.Span(id = "strat-pavimento-concreto-desc")),
                                    target="check-strat-pavimento-concreto",
                                    trigger="hover",
                                ),
                            ],
                            style={"display": "inline"},
                        ),
                        "value": "strat-pavimento-concreto",
                    },
                    {
                        "label": html.Div(
                            [
                                html.P(
                                    html.Span(id = "strat-pavimento-reflector-title"),
                                    id="check-strat-pavimento-reflector",
                                    style={"display": "inline"},
                                ),
                                dbc.Popover(
                                    dbc.PopoverBody(html.Span(id = "strat-pavimento-reflector-desc")),
                                    target="check-strat-pavimento-reflector",
                                    trigger="hover",
                                ),
                            ],
                            style={"display": "inline"},
                        ),
                        "value": "strat-pavimento-reflector",
                    },
                ],
                value=[],
                id="strategy-checklist",
                inputStyle={"margin-right": "10px"},
                labelStyle={"display": "block", "margin-bottom": "15px"},
            ),
        ),
    ]
)


legend_colors = {
    "Muy frío": "#2166AC",
    "Frío": "#67A9CF",
    "Ligeramente frío": "#D1E5F0",
    "Templado": "#F7F7F7",
    "Ligeramente cálido": "#FDDBC7",
    "Caliente": "#EF8A62",
    "Muy caliente": "#B2182B",
}

map_legend = html.Div(
    [
        html.Div(
            [
                html.Div(
                    "",
                    style={
                        "height": "10px",
                        "width": "10px",
                        "backgroundColor": legend_colors["Muy frío"],
                        "margin-right": "5px",
                    },
                ),
                html.Div(
                    html.Span(id="color-muy-frio"),
                    className="font-weight-light text-white",
                    style={"font-size": "13px"},
                ),
            ],
            className="d-flex align-items-center m-1",
        ),
        html.Div(
            [
                html.Div(
                    "",
                    style={
                        "height": "10px",
                        "width": "10px",
                        "backgroundColor": legend_colors["Frío"],
                        "margin-right": "5px",
                    },
                ),
                html.Div(
                    html.Span(id="color-frio"),
                    className="font-weight-light text-white",
                    style={"font-size": "13px"},
                ),
            ],
            className="d-flex align-items-center m-1",
        ),
        html.Div(
            [
                html.Div(
                    "",
                    style={
                        "height": "10px",
                        "width": "10px",
                        "backgroundColor": legend_colors["Ligeramente frío"],
                        "margin-right": "5px",
                    },
                ),
                html.Div(
                    html.Span(id="color-ligeramente-frio"),
                    className="font-weight-light text-white",
                    style={"font-size": "13px"},
                ),
            ],
            className="d-flex align-items-center m-1",
        ),
        html.Div(
            [
                html.Div(
                    "",
                    style={
                        "height": "10px",
                        "width": "10px",
                        "backgroundColor": legend_colors["Templado"],
                        "margin-right": "5px",
                    },
                ),
                html.Div(
                    html.Span(id="color-templado"),
                    className="font-weight-light text-white",
                    style={"font-size": "13px"},
                ),
            ],
            className="d-flex align-items-center m-1",
        ),
        html.Div(
            [
                html.Div(
                    "",
                    style={
                        "height": "10px",
                        "width": "10px",
                        "backgroundColor": legend_colors["Ligeramente cálido"],
                        "margin-right": "5px",
                    },
                ),
                html.Div(
                    html.Span(id="color-ligeramente-calido"),
                    className="font-weight-light text-white",
                    style={"font-size": "13px"},
                ),
            ],
            className="d-flex align-items-center m-1",
        ),
        html.Div(
            [
                html.Div(
                    "",
                    style={
                        "height": "10px",
                        "width": "10px",
                        "backgroundColor": legend_colors["Caliente"],
                        "margin-right": "5px",
                    },
                ),
                html.Div(
                    html.Span(id="color-caliente"),
                    className="font-weight-light text-white",
                    style={"font-size": "13px"},
                ),
            ],
            className="d-flex align-items-center m-1",
        ),
        html.Div(
            [
                html.Div(
                    "",
                    style={
                        "height": "10px",
                        "width": "10px",
                        "backgroundColor": legend_colors["Muy caliente"],
                        "margin-right": "5px",
                    },
                ),
                html.Div(
                    html.Span(id="color-muy-caliente"),
                    className="font-weight-light text-white",
                    style={"font-size": "13px"},
                ),
            ],
            className="d-flex align-items-center m-1",
        ),
    ],
    className="d-flex justify-content-around flex-column",
    style={"width": "fit-content", "backgroundColor": "rgba(0,0,0,0.35)"},
)


map = html.Div(
    [
        html.Div(map_legend, className="position-absolute fixed-bottom right-0"),
        dcc.Graph(style={"height": "100%"}, id="suhi-graph-temp-map"),
    ],
    className="position-relative",
    style={"height": "100%"},
)

plots = html.Div(
    [
        dbc.Row(
            [
                figureWithDescription_translation2( # Version modificada para HISTOGRAMA_TEXT
                    dcc.Graph(id="suhi-graph-areas"),
                    HISTOGRAMA_TEXT,
                    "title1"
                ),
                
                figureWithDescription_translation(
                    dcc.Graph(id="suhi-graph-temp-lc"),
                    "BARS_TEXT",
                    "title2",
                ),
                figureWithDescription_translation(
                    dcc.Graph(id="suhi-graph-radial-temp"),
                    "empty-desc1",
                    "title3",
                ),
                figureWithDescription_translation(
                    dcc.Graph(id="suhi-graph-radial-lc"),
                    "empty-desc2",
                    "title4",
                ),
            ],
            style={"overflow": "scroll", "height": "82vh"},
        ),
    ],
    id="plots",
)

welcomeAlert = dbc.Alert(WELCOME_CONTENT, color="secondary")
mapIntroAlert = dbc.Alert(id = "MAP_INTRO_TEXT", color="light")

tabs = [
    dbc.Tab(
        html.Div(
            [
                html.Div(
                    [
                        html.P(id = "temperature", style=SUBTITLE_STYLE),
                        html.P(
                            id="suhi-p-urban-temp",
                            style=MEAN_TEMPERATURE_STYLE,
                        ),
                        html.P(
                            [
                                html.Span(id="satellite_image_data"),
                                html.A(
                                    "USGS Landsat 8 Level 2, Collection 2, Tier 1",
                                    href=(
                                        "https://developers.google.com/earth-engine"
                                        "/datasets/catalog/LANDSAT_LC08_C02_T1_L2"
                                    ),
                                ),
                            ],
                            style={"fontSize": "0.8rem"},
                        ),
                    ],
                    style={"margin-bottom": "15px"},
                ),
                strategyList,
                impactView,
            ],
        ),
        label="Controles",
        id="tab-controls-suhi",
        tab_id="tabControls",
    ),
    dbc.Tab(
        plots,
        label="Gráficas",
        id="tab-plots-suhi",
        tab_id="tabPlots",
    ),
    dbc.Tab(
        html.Div([welcomeAlert, mapIntroAlert]),
        label="Info",
        id="tab-info-suhi",
        tab_id="tabInfo",
    ),
    dbc.Tab(
        [
            generate_drive_text_translation(
                how="La información procesada en la sección Islas de Calor se realiza incluyendo Google Earth Engine. De esta manera, la descarga de los datos empleados, debido a su tamaño, es a través del Google Drive de la cuenta empleada en la autenticación de Google Earth Engine en el caso del raster y al disco local en el caso de los datos tabulares para hacer la visualizaciones.",
                where="La descarga del raster con nombre 'suhi_raster.tif' se hará al directorio raíz del Google Drive de la cuenta empleada. Por otro lado, el archivo descargado a disco es 'city-country-suhi-data.csv', reemplazando 'city' por la ciudad y 'country' por el país analizado, respectivamente.",
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    #"Descargar rasters",
                                    id="suhi-btn-download-rasters",
                                    color="light",
                                    title="Descarga los archivos Raster a Google Drive. En este caso la información es procesada en Google Earth Engine y la única opción de descarga es al directorio raíz de tu Google Drive.",
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    #"Cancelar ejecución",
                                    id="suhi-btn-stop-task",
                                    color="danger",
                                    style={"display": "none"},
                                ),
                                width=4,
                            ),
                        ],
                        justify="center",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    #"Descargar CSV",
                                    id="suhi-btn-download-csv",
                                    color="light",
                                    title="Descarga el archivo .csv, que alimenta las visualizaciones, localmente en tu carpeta de Descargas.",
                                ),
                                width=4,
                            ),
                            dbc.Col(width=4),
                        ],
                        justify="center",
                    ),
                    dbc.Row(
                        dbc.Col(html.Span(id="suhi-span-rasters-output"), width=3),
                        justify="center",
                    ),
                ],
            ),
        ],
        label="Descargables",
        id = "tabDownloadables-suhi",
    ),
]

# Traduccion

language_buttons = dbc.ButtonGroup(
    [
        dbc.Button("Español", id="btn-lang-es", n_clicks=0),
        dbc.Button("English", id="btn-lang-en", n_clicks=0),
        dbc.Button("Portuguese", id="btn-lang-pt", n_clicks=0),
    ],
    style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1"},
)

layout = new_page_layout(
    [map],
    tabs,
    stores=[
        dcc.Store("suhi-store-task-name"),
        dcc.Interval(id="suhi-interval", interval=10000, n_intervals=0, disabled=True),
        dcc.Download(id="download-dataframe-csv"),
        dcc.Location(id="suhi-location"),
    ],
    alerts=[
        dbc.Alert(
            "Algunas gráficas no pudieron ser generadas. Considere cambiar la bounding box de análisis.",
            id="suhi-alert",
            is_open=False,
            dismissable=True,
            color="warning",
        )
    ],
)

# ---

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
    [Output(key, 'label') for key in tab_translations.keys()], 
    [Input('btn-lang-es', 'n_clicks'),
     Input('btn-lang-en', 'n_clicks'),
     Input('btn-lang-pt', 'n_clicks')]
)
def update_tab_labels(btn_lang_es, btn_lang_en, btn_lang_pt):
    ctx = dash.callback_context

    if not ctx.triggered:
        language = 'es'  # Idioma predeterminado
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        language = 'es' if button_id == 'btn-lang-es' else 'en' if button_id == 'btn-lang-en' else 'pt'

    tab_labels = [tab_translations[key][language] for key in tab_translations.keys()]

    return tab_labels  

# ---


@callback(
    Output("impact-result-square-kilometers", "children"),
    Output("impact-result-kilometers", "children"),
    Output("impact-result-degrees", "children"),
    Output("impact-mitigated-degrees", "children"),
    Output("suhi-p-urban-temp", "children"),
    Output("suhi-location", "pathname"),
    Output("suhi-alert", "is_open"),
    Input("strategy-checklist", "value"),
    State("global-store-hash", "data"),
    State("global-store-bbox-latlon", "data"),
    State("global-store-uc-latlon", "data"),
)
def update_mitigation_kilometers(values, id_hash, bbox_latlon, uc_latlon):
    if id_hash is None:
        return [dash.no_update] * 5 + ["/", dash.no_update]

    path_cache = Path(f"./data/cache/{id_hash}")

    bbox_latlon = shape(bbox_latlon)
    uc_latlon = shape(uc_latlon)

    bbox_mollweide = ug.reproject_geometry(bbox_latlon, "ESRI:54009")
    uc_mollweide = ug.reproject_geometry(uc_latlon, "ESRI:54009")

    try:
        df = ht.load_or_get_mit_areas_df(
            bbox_latlon, bbox_mollweide, uc_mollweide.centroid, path_cache
        )
    except Exception:
        return [dash.no_update] * 6 + [True]

    urban_mean_temp = ht.get_urban_mean(bbox_latlon, "Qall", 2022, path_cache)

    area_roofs = df.roofs.item()
    area_urban = df.urban.item()
    roads_distance = df.roads.item()

    mitigatedDegrees = 0
    impactedSquareKm = 0
    impactedKm = 0

    for strategyId in values:
        mitigatedDegrees += STRATEGIES[strategyId]["mitigation"]
        areaFraction = STRATEGIES[strategyId]["area_fraction"]
        if (
            strategyId == "strat-pavimento-concreto"
            or strategyId == "strat-pavimento-reflector"
        ):
            impactedKm += roads_distance
        elif (
            strategyId == "strat-techos-verdes" or strategyId == "strat-techos-frescos"
        ):
            impactedSquareKm += area_roofs * areaFraction
        elif strategyId == "strat-vegetacion":
            impactedSquareKm += area_urban * areaFraction

    mitigatedUrbanTemperature = urban_mean_temp - mitigatedDegrees

    return (
        f"{int(round(impactedSquareKm, 0))} Km²",
        f"{int(round(impactedKm, 0))} Km",
        format_temp(mitigatedUrbanTemperature),
        format_temp(mitigatedDegrees),
        format_temp(urban_mean_temp),
        dash.no_update,
        dash.no_update,
    )


@callback(
    Output("download-dataframe-csv", "data"),
    Input("suhi-btn-download-csv", "n_clicks"),
    State("global-store-hash", "data"),
    prevent_initial_call=True,
)
def download_file(n_clicks, id_hash):
    path_cache = Path(f"./data/cache/{id_hash}")
    csv_path = path_cache / "land_cover_by_temp.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        return dcc.send_data_frame(df.to_csv, "suhi_data.csv")


@callback(
    Output("suhi-interval", "disabled", allow_duplicate=True),
    Output("suhi-store-task-name", "data"),
    Output("suhi-btn-stop-task", "style", allow_duplicate=True),
    Output("suhi-span-rasters-output", "children", allow_duplicate=True),
    Input("suhi-btn-download-rasters", "n_clicks"),
    State("global-store-hash", "data"),
    State("global-store-bbox-latlon", "data"),
    State("suhi-store-task-name", "data"),
    prevent_initial_call=True,
)
def start_download(n_clicks, id_hash, bbox_latlon, task_name):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update, dash.no_update, dash.no_update

    path_cache = Path(f"./data/cache/{id_hash}")

    if task_name is None:
        start_date, end_date = du.date_format("Qall", 2022)

        bbox_latlon = shape(bbox_latlon)
        bbox_ee = ru.bbox_to_ee(bbox_latlon)
        
        lst, proj = ht.get_lst(bbox_ee, start_date, end_date)
        _, masks = wc.get_cover_and_masks(bbox_ee, proj)

        img_cat = ht.get_cat_suhi(lst, masks, path_cache)

        task = ee.batch.Export.image.toDrive(
            image=img_cat,
            description="suhi_raster",
            scale=img_cat.projection().nominalScale(),
            region=bbox_ee,
            crs=img_cat.projection(),
            fileFormat="GeoTIFF",
        )
        task.start()
        status = task.status()

        return (False, status["name"], {"display": "block"}, "Iniciando descarga")
    else:
        return (dash.no_update, dash.no_update, dash.no_update, dash.no_update)


@callback(
    Output("suhi-span-rasters-output", "children", allow_duplicate=True),
    Output("suhi-interval", "disabled", allow_duplicate=True),
    Input("suhi-interval", "n_intervals"),
    State("suhi-store-task-name", "data"),
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
    Output("suhi-graph-temp-map", "figure"),
    Output("suhi-graph-areas", "figure"),
    Output("suhi-graph-temp-lc", "figure"),
    Output("suhi-graph-radial-temp", "figure"),
    Output("suhi-graph-radial-lc", "figure"),
    Input("global-store-hash", "data"),
    Input("global-store-bbox-latlon", "data"),
    Input("global-store-fua-latlon", "data"),
    Input("global-store-uc-latlon", "data"),
    Input('btn-lang-es', 'n_clicks'),
    Input('btn-lang-en', 'n_clicks'),
    Input('btn-lang-pt', 'n_clicks'),
)
def generate_maps(id_hash, bbox_latlon, fua_latlon, uc_latlon, btn_lang_es, btn_lang_en, btn_lang_pt):
    if id_hash is None:
        return [dash.no_update] * 5
    
    ctx = dash.callback_context
    if not ctx.triggered:
        language = 'es'  # Idioma predeterminado
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        language = 'es' if button_id == 'btn-lang-es' else 'en' if button_id == 'btn-lang-en' else 'pt'

    path_cache = Path(f"./data/cache/{id_hash}")

    bbox_latlon = shape(bbox_latlon)
    fua_latlon = shape(fua_latlon)
    uc_latlon = shape(uc_latlon)
    bbox_ee = ru.bbox_to_ee(bbox_latlon)

    start_date, end_date = ht.date_format(SEASON, YEAR)

    try:
        lst, proj = ht.get_lst(bbox_ee, start_date, end_date)

        _, masks = wc.get_cover_and_masks(bbox_ee, proj)

        img_cat = ht.get_cat_suhi(lst, masks, path_cache)
        df_t_areas = ht.load_or_get_t_areas(bbox_ee, img_cat, masks, path_cache)
        df_land_usage = ht.load_or_get_land_usage_df(bbox_ee, img_cat, path_cache)

        temp_map = pht.plot_cat_map(
            bbox_ee, fua_latlon.centroid, img_cat
        )
        areas_plot = pht.plot_temp_areas(df_t_areas, language=language) # 
        
        temps_by_lc_plot = pht.plot_temp_by_lc(df_land_usage, language=language) #
        
    except Exception as e:
        temp_map = dash.no_update
        areas_plot = dash.no_update
        temps_by_lc_plot = dash.no_update        

    df_f, df_lc = ht.load_or_get_radial_distributions(bbox_latlon, uc_latlon, start_date, end_date, path_cache)
    
    radial_temp_plot = pht.plot_radial_temperature(df_f, language=language) #
    radial_lc_plot = pht.plot_radial_lc(df_lc, language=language) #

    return temp_map, areas_plot, temps_by_lc_plot, radial_temp_plot, radial_lc_plot


@callback(
    Output("suhi-btn-stop-task", "style"),
    Output("suhi-interval", "disabled"),
    Output("suhi-span-rasters-output", "children"),
    Input("suhi-btn-stop-task", "n_clicks"),
    State("suhi-store-task-name", "data"),
    prevent_initial_call=True,
)
def stop_task(n_clicks, task_id):
    ee.data.cancelOperation(task_id)
    return {"display": "none"}, True, "Descarga cancelada"