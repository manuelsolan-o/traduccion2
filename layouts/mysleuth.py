import json
import os
import requests

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import xarray as xr

from dash import html
from dash import dcc
from pathlib import Path
from shapely.geometry import shape

def calculate_coverage(worldcover, sleuth_predictions, start_year):
    world_cover_type = {
        "Tree Cover": 10,
        "Shrubland": 20,
        "Grassland": 30,
        "Cropland": 40,
        "Built-up": 50,
        "Bare/Sparse Vegetation": 60,
        "Snow and Ice": 70,
        "Permanent water bodies": 80,
        "Herbaceous wetlands": 90,
        "Mangroves": 95,
        "Moss and lichen": 100,
    }

    # Obtener el tamaño de sleuth_predictions
    num_samples, height, width = sleuth_predictions.shape

    # Crear un diccionario de kernels
    kernels = {}
    for key, value in world_cover_type.items():
        kernels[key] = np.where(worldcover == value, 1, 0)

    # Inicializar un DataFrame vacío
    result_df = pd.DataFrame()

    # Aplicar el proceso a cada clase en world_cover_type
    for key, kernel in kernels.items():
        sample_results = []
        for i in range(num_samples):
            result = np.sum((1 - sleuth_predictions[i]) * kernel) / (height * width)
            sample_results.append(result)
        result_df[key] = sample_results

    sample_results = []
    for i in range(num_samples):
        result = np.sum(sleuth_predictions[i]) / (height * width)
        sample_results.append(result)
    result_df["Urban"] = sample_results
    result_df["Year"] = list(range(start_year + 1, start_year + num_samples + 1))
    result_df.set_index("Year", inplace=True)
    result_df = result_df * 100
    return result_df

def plot_coverage2(lc_df, title):
    # Eliminamos columnas que tengan cero
    lc_df = lc_df.loc[:, (lc_df != 0).any(axis=0)]

    # Ordenamos columnas
    column_names_sorted = lc_df.iloc[0].sort_values(ascending=False).index
    lc_df = lc_df[column_names_sorted]

    # "Urban" se convierte en la primera columna
    wanted_cols = ["Urban"] + [col for col in lc_df.columns if (col != "Urban") and (col != "Year")]
    lc_df = lc_df[wanted_cols]
    lc_df["Año"] = list(range(2021, 2071))

    fig = px.area(lc_df, x="Año", y=wanted_cols, color_discrete_map=WORLD_COVER_COLOR, markers=True)

    fig.update_layout(
        title=title,
        yaxis_title="Porcentaje",
        xaxis_title="Año",
        legend_title="Tipo de cobertura",
        hovermode="x",
    )

    fig.update_traces(hovertemplate="%{y:.2f}<extra></extra>")

    return fig

def plot_coverage(lc_df, title, language='es'):
    translations = {
        "es": {
            "year": "Año",
            "percentage": "Porcentaje",
            "coverage_type": "Tipo de Cobertura",
            "urban": "Urbano"
        },
        "en": {
            "year": "Year",
            "percentage": "Percentage",
            "coverage_type": "Type of Coverage",
            "urban": "Urban"
        },
        "pt": {
            "year": "Ano",
            "percentage": "Percentagem",
            "coverage_type": "Tipo de Cobertura",
            "urban": "Urbano"
        }
    }
    
    column_name_mapping = {
        "Urban": translations[language]['urban'],
        "Year": translations[language]['year']
    }

    # Renombrar columnas
    lc_df = lc_df.rename(columns=column_name_mapping)

    # Eliminamos columnas que tengan cero
    lc_df = lc_df.loc[:,(lc_df != 0).any(axis=0)]
    
    column_names_sorted = lc_df.iloc[0].sort_values(ascending=False).index
    lc_df = lc_df[column_names_sorted]

    urban_translation = translations[language]['urban']
    wanted_cols = [urban_translation] + [col for col in lc_df.columns if (col != urban_translation) and (col != translations[language]['year'])]
    lc_df = lc_df[wanted_cols]
    lc_df[translations[language]['year']] = list(range(2021, 2071))

    fig = px.area(lc_df, x=translations[language]['year'], y=wanted_cols, markers=True)

    fig.update_layout(
        title=title,
        yaxis_title=translations[language]['percentage'],
        xaxis_title=translations[language]['year'],
        legend_title=translations[language]['coverage_type'],
        hovermode="x",
        )
    fig.update_traces(hovertemplate="%{y:.2f}<extra></extra>")

    return fig

def plot_sleuth_predictions(grid, start_year, num_years, language='es'):
    translations = {
        "es": {
            "year": "Año",
            "urbanization_probability": "Probabilidad de Urbanización"
        },
        "en": {
            "year": "Year",
            "urbanization_probability": "Urbanization Probability"
        },
        "pt": {
            "year": "Ano",
            "urbanization_probability": "Probabilidade de Urbanização"
        }
    }

    sim_years = list(range(start_year + 1, start_year + num_years + 1))

    grid_plot = xr.DataArray(
        data=grid * 100,
        dims=[translations[language]['year'], "y", "x"],
        coords={
            translations[language]['year']: sim_years,
            "y": list(range(grid.shape[1])),
            "x": list(range(grid.shape[2])),
        },
    )

    fig = px.imshow(
        grid_plot,
        animation_frame=translations[language]['year'],
        labels=dict(color=translations[language]['urbanization_probability']),
        zmin=0,
        zmax=100,
        aspect="equal",
    )
    fig.update_xaxes(showticklabels=False, visible=False)
    fig.update_yaxes(showticklabels=False, visible=False)
    return fig

def load_sleuth_predictions(path_cache, id_hash, mode):
    num_years = 50  # Número de años de predicción
    num_rows, num_cols = 100, 100  # Dimensiones espaciales

    # Crear una matriz tridimensional con valores aleatorios
    # Dimensiones: años, filas, columnas
    return np.random.rand(num_years, num_rows, num_cols)

def plot_sleuth_predictions2(grid, start_year, num_years):
    sim_years = list(range(start_year + 1, start_year + num_years + 1))

    grid_plot = xr.DataArray(
        data=grid * 100,
        dims=["Año", "y", "x"],
        coords={
            "Año": sim_years,
            "y": list(range(grid.shape[1])),
            "x": list(range(grid.shape[2])),
        },
    )

    fig = px.imshow(
        grid_plot,
        animation_frame="Año",
        labels=dict(color="Probabilidad de urbanización"),
        zmin=0,
        zmax=100,
        aspect="equal",
    )
    fig.update_xaxes(showticklabels=False, visible=False)
    fig.update_yaxes(showticklabels=False, visible=False)
    return fig


WORLD_COVER_COLOR = {
    "Tree Cover": "#006400",
    "Shrubland": "#ffbb22",
    "Grassland": "#ffff4c",
    "Cropland": "#f096ff",
    "Built-up": "#fa0000",
    "Bare/Sparse Vegetation": "#b4b4b4",
    "Snow and Ice": "#f0f0f0",
    "Permanent water bodies": "#0064c8",
    "Herbaceous wetlands": "#0096a0",
    "Mangroves": "#00cf75",
    "Moss and lichen": "#fae6a0",
}

FIELDS = ["diffusion", "breed", "spread", "slope", "road"]

import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.express as px
from pathlib import Path

def summary(id_hash, urban_rasters, years, language='es'):
    
    translations = {
        "es": {
        "year": "Año",
        "urbanization_percentage": "Porcentaje de Urbanización",
        "category": "Categoría",
        "observations": "Observaciones",
        "expansion": "Expansión",
        "general_summary": "Resumen General",
        "urban_area_increase": "+{0:.1f}% de aumento del área urbanizada 2070 vs. 2020.",
        "modes": ["inercial", "acelerada", "controlada"]
        },
        "en": {
        "year": "Year",
        "urbanization_percentage": "Urbanization Percentage",
        "category": "Category",
        "observations": "Observations",
        "expansion": "Expansion",
        "general_summary": "General Summary",
        "urban_area_increase": "+{0:.1f}% increase in urban area 2070 vs. 2020.",
        "modes": ["inertial", "accelerated", "controlled"]
        },
        "pt": {
        "year": "Ano",
        "urbanization_percentage": "Percentagem de Urbanização",
        "category": "Categoria",
        "observations": "Observações",
        "expansion": "Expansão",
        "general_summary": "Resumo Geral",
        "urban_area_increase": "+{0:.1f}% de aumento da área urbana 2070 vs. 2020.",
        "modes": ["inercial", "acelerada", "controlada"]
        }
    }

    path_cache = Path(f"./data/cache/{id_hash}")
    worldcover = np.random.rand(100, 100)  # Suponiendo que esta es la forma de obtener worldcover
    start_year = 2020
    num_years = 50

    id_hash = str(id_hash)
    historical_years = np.array(years)
    historical_grids = np.array(urban_rasters)
    
    modes_translated = translations[language]['modes']
    
    x = list(historical_years)
    y = [grid.sum() / grid.size for grid in historical_grids]
    z = [translations[language]['observations']] * len(x)
    final_y = y[-1]

    tabs = []
    coverage_graphs = []
    for mode in modes_translated:
        grids = load_sleuth_predictions(path_cache, id_hash, mode=mode)

        x_pred = list(range(start_year + 1, start_year + num_years + 1))
        y_pred = [grid.sum() / grid.size for grid in grids]
        z_pred = [f"{translations[language]['expansion']} {mode}"] * len(x_pred)

        x_pred = [start_year] + x_pred
        y_pred = [final_y] + y_pred

        x.extend(x_pred)
        y.extend(y_pred)
        z.extend(z_pred)

        # Plot Sleuth Predictions
        tab = dbc.Tab(
            dbc.Card(
                dbc.CardBody(
                    dbc.Container(
                        dbc.Row(
                            dbc.Col(
                                dcc.Graph(
                                    figure=plot_sleuth_predictions(grids, 2020, 50, language = language),
                                    responsive=True,
                                    style={"height": "60vh"},
                                ),
                                width=8,
                            )
                        )
                    )
                )
            ),
            label=f"{translations[language]['expansion']}: {mode}",
        )
        tabs.append(tab)

        # Coverage
        estimate_coverage = calculate_coverage(worldcover, grids, start_year)
        fig_coverage = plot_coverage(estimate_coverage, f"{translations[language]['expansion']}: {mode}", language = language)
        coverage_graphs.append(dcc.Graph(figure=fig_coverage))

    df = pd.DataFrame(
        zip(x, y, z), columns=[translations[language]['year'], translations[language]['urbanization_percentage'], translations[language]['category']]
    )
    fig = px.line(df, x=translations[language]['year'], y=translations[language]['urbanization_percentage'], color=translations[language]['category'])
    fig.update_yaxes(tickformat=",.0%")

    # Cambio Porcentual por Escenario
    base = df.loc[(df[translations[language]['year']] == 2020) & (df[translations[language]['category']] == translations[language]['observations'])][    translations[language]['urbanization_percentage']
    ].values[0]

    columns = []
    #for mode in modes_translated:
    for cat, color in zip(
        modes_translated, ["danger", "warning", "success"]
    ):
        c = cat
        cat = f"{translations[language]['expansion']} {cat}"#.capitalize()}"
        #prediction = df.loc[df[translations[language]['category']] == cat][translations[language]['urbanization_percentage']].values[0]
        prediction = df.loc[df[translations[language]['category']] == cat][translations[language]['urbanization_percentage']].values[0]

        percentage_increase = round(((prediction - base) / base) * 100, 1)
        col = dbc.Col(dbc.Card(
            dbc.CardBody(
                [
                    html.H5(f"{translations[language]['expansion']}: {c}", className="card-title"),
                    html.P(
                        f"+{percentage_increase}% {translations[language]['urban_area_increase'].format(percentage_increase)}",
                        className="card-text",
                    ),
                ]
            ),
            color=color,
            inverse=True,
        ))
        
        columns.append(col)

    cards = html.Div(dbc.Row(columns, className="mb-4"))
    all_elements = [cards] + coverage_graphs + [dcc.Graph(figure=fig)]
    plot_tab = dbc.Tab(dbc.Card(dbc.CardBody(all_elements)), label=translations[language]["general_summary"])
    tabs = [plot_tab] + tabs
    out = dbc.Tabs(tabs, active_tab="tab-0")

    return out
