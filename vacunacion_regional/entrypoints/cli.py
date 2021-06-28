from click.decorators import option
from vacunacion_regional.data_management.postprocessing import generate_tables
from vacunacion_regional.entrypoints.api import get_from_data_parameters, save_parameters_as_file
from pathlib import Path
from click import command, argument
from halo import Halo
from spinners import Spinners
from vacunacion_regional.model.main import get_model


@command()
@argument("source_path", required=True)
@option("--save", "save", flag_value=True, default=False)
@option("--output", "output_path", default="out.mst")
def cli_entrypoint(source_path: str, output_path, save):
    config, mappings = get_from_data_parameters(source_path=source_path)
    save_parameters_as_file(config)
    model = get_model(config)
    with Halo(text='Optimizing\n', spinner=Spinners.dots.value) as spinner:
        model.optimize()
        spinner.succeed('Optimized\n')
    with Halo(text='Showing variables\n', spinner=Spinners.dots.value) as spinner:
        model.printAttr("X")
        if save:
            generate_tables(model, mappings=mappings, save=save)
        spinner.succeed('Printted all variables\n')
    if save:
        output_path = Path(output_path).absolute()
        model.write(str(output_path))
    model.printStats()
