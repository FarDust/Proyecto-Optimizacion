import json

from pandas import json_normalize

# https://towardsdatascience.com/easy-steps-to-plot-geographic-data-on-a-map-python-11217859a2db


def get_info_comuna(comuna):
    comunas = json.load(open("comunas.json", encoding="utf-8"))

    comunas = comunas["features"]

    data = json_normalize(comunas)
    data = data.set_index("attributes.CUT_COM")
    focus_data = data[data["attributes.REGION"] == "Biobío"]
    return focus_data
