from json import dump
from pathlib import Path
from click import command, argument
from halo import Halo
from spinners import Spinners
from vacunacion_regional.data_management.vaccines import process_data_from_file, get_params
from vacunacion_regional.model.main import get_model
from vacunacion_regional.model.parameters import ParametersConfig

@command()
@argument("source_path", required=True)
def cli_entrypoint(source_path):
    data_path = Path(source_path).absolute()
    data = process_data_from_file(data_path)
    params = get_params(data)
    params.pop("mappings")
    config = ParametersConfig(**params)
    dump(config.__dict__, open('params.json', 'w'))
    model = get_model(config)
    with Halo(text='Optimizing', spinner=Spinners.dots.value):
        model.optimize()
    with Halo(text='Showing variables', spinner=Spinners.dots.value):
        model.printAttr("X")
    model.printStats()