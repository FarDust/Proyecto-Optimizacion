import json
import pandas as pd


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


with open("../data_management/vacunas.json", "r") as file:
    filedata = file.read()

vaccines = json.loads(filedata)

data = pandification(vaccines)


# Eliminamos comunas extremas
extreme_zone = [
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

extreme_index = get_index(data, extreme_zone)
data = data.drop(extreme_index, axis=0).reset_index()


data["P_DOSIS_1"] = data["DOSIS_1"] / data["POB_OBJ"]
data["P_DOSIS_2"] = data["DOSIS_2"] / data["POB_OBJ"]
data["P_DOSIS"] = data["DOSIS_TOT"] / (2 * data["POB_OBJ"])

print(data.shape())
