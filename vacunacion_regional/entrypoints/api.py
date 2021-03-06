

from json import dump
from pathlib import Path
from typing import Dict, Tuple
from vacunacion_regional.setting import OUTPUTS_PATH
from vacunacion_regional.data_management.vaccines import get_params, process_data_from_file
from vacunacion_regional.data_management.postprocessing import get_porcentajes_vacunacion_plot, get_porcentajes_vacunacion_target_plot
from vacunacion_regional.data_management.postprocessing import process_model_variables, get_mapped_variables
from vacunacion_regional.model.main import get_model
from vacunacion_regional.model.parameters import ParametersConfig
from gurobipy import Model
import matplotlib.pyplot as plt
import pandas as pd

__all__ = [
    "obtain_model",
    "get_from_data_parameters",
    "get_default_parameters",
    "save_parameters_as_file"
    ]


def obtain_model(parameters: ParametersConfig) -> Model:
    return get_model(parameters)


def get_from_data_parameters(source_path: str) -> Tuple[ParametersConfig, Dict]:
    data_path = Path(source_path).absolute()
    data = process_data_from_file(data_path)
    params = get_params(data)
    mappings = params.pop("mappings")
    config = ParametersConfig(**params)
    return config, mappings


def get_default_parameters() -> Tuple[ParametersConfig, Dict]:
    config = ParametersConfig()
    return config, None


def save_parameters_as_file(parameters: ParametersConfig, experiment=0) -> None:
    dump(parameters.__dict__, Path(OUTPUTS_PATH, f"params_{experiment}.json").open('w'), indent=4, sort_keys=True)


def save_plots(model: Model, mappings: dict, experiment=0):
    mapped_variables = get_mapped_variables(model)
    variables = process_model_variables(mapped_variables)
    data = pd.json_normalize(variables['porcentajes_comuna_dia'])
    data['comuna'] = data['comuna'].map(mappings['comunas'])
    plot = get_porcentajes_vacunacion_plot(variables, mappings)
    plot_path = Path(OUTPUTS_PATH, 'plots')
    if not plot_path.exists():
        plot_path.mkdir()
    plt.savefig(str(Path(plot_path, f"by_comuna_{experiment}.png")), bbox_inches='tight')
    plt.clf()
    plot2 = get_porcentajes_vacunacion_target_plot(variables, mappings)
    plt.savefig(str(Path(plot_path, f"median_with_var_{experiment}.png")), bbox_inches='tight')
    plt.clf()