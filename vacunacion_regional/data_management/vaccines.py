import json
from pathlib import Path
import pandas as pd
from pandas.core.frame import DataFrame


# Eliminamos comunas extremas
EXTREME_ZONES = [
    "Isla de Pascua",
    "Juan Fernández",
    "Antártica",
    "Cabo de Hornos",
    "Porvenir",
    "Primavera",
    "Timaukel",
    "Laguna Blanca",
    "Punta Arenas",
    "Río Verde",
    "San Gregorio",
    "Natales",
    "Torres del Paine",
]


def pandification(my_json):
    data = []
    for commune in my_json["features"]:
        row = commune["attributes"]
        data.append(row)
    return pd.DataFrame(data)


def get_index(data, elements):
    index = []
    for e in elements:
        index.append(data[data["COMUNA"] == e].index[0])
    return index


def process_data_from_file(path: Path):
    with open(str(path), "r", encoding="utf-8") as file:
        filedata = file.read()

    vaccines = json.loads(filedata)

    data = pandification(vaccines)

    extreme_index = get_index(data, EXTREME_ZONES)
    data = data.drop(extreme_index, axis=0).reset_index()

    data["POB_OBJ"] = 2 * data["POB_OBJ"]
    data["P_VACUNADOS"] = data["DOSIS_TOT"]

    return data


def get_params(data: DataFrame, region=None):
    data = data[data['REGION'] == "Arica y Parinacota"]
    data_parameters = {
        "mappings": dict()
    }

    comunas_series = data['COMUNA']
    comunas_names = comunas_series.unique()
    comunas = list(range(comunas_names.shape[0]))
    comunas_reverse_mapping = {
        comuna_index: comunas_names[comuna_index]
        for comuna_index in range(len(comunas))
        }

    poblacion_objetivo = list()
    for comuna in comunas:
        comuna_name = comunas_reverse_mapping[comuna]
        poblacion_objetivo_comuna = int(data[
            data['COMUNA'] == comuna_name
            ]['POB_OBJ'])
        poblacion_objetivo.append(poblacion_objetivo_comuna)
    poblacion_objetivo = tuple(poblacion_objetivo)

    poblacion_vacunada = list()
    for comuna in comunas:
        comuna_name = comunas_reverse_mapping[comuna]
        poblacion_objetivo_comuna = int(data[
            data['COMUNA'] == comuna_name
            ]['P_VACUNADOS'])
        poblacion_vacunada.append(poblacion_objetivo_comuna)

    data_parameters.update({"comunas": comunas})
    data_parameters.update({"poblacion_objetivo": tuple(poblacion_objetivo)})
    data_parameters.update({"poblacion_vacunada": tuple(poblacion_vacunada)})
    data_parameters["mappings"].update({"comunas": comunas_reverse_mapping})

    return data_parameters
