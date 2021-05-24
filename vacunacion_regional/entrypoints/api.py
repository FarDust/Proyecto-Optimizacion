

from json import dump
from pathlib import Path
from typing import Dict, Tuple
from vacunacion_regional.data_management.vaccines import get_params, process_data_from_file
from vacunacion_regional.model.main import get_model
from vacunacion_regional.model.parameters import ParametersConfig
from gurobipy import Model

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


def save_parameters_as_file(parameters: ParametersConfig) -> None:
    dump(parameters.__dict__, open('params.json', 'w'))