import sys
import shutil
from vacunacion_regional.model.parameters import parametersRandomizer
from vacunacion_regional.setting import OUTPUTS_PATH
from click.decorators import option
from vacunacion_regional.data_management.postprocessing import generate_tables
from vacunacion_regional.entrypoints.api import get_from_data_parameters, save_parameters_as_file, save_plots
from pathlib import Path
from click import command, argument
from halo import Halo
from spinners import Spinners
from vacunacion_regional.model.main import get_model


@command()
@argument("source_path", required=True)
@option("--save", "save", flag_value=True, default=False)
@option("--output", "output_path", default="out.mps")
@option("--experiments", "experiments", default=1)
@option("--attribute", "attribute", default='camiones')
@option("--random", "is_random_experiment", flag_value=True, default=False)
def cli_entrypoint(source_path: str, output_path, save, experiments, is_random_experiment, attribute):
    config, mappings = get_from_data_parameters(source_path=source_path)
    randomizer = parametersRandomizer(config)
    stats_path = Path(OUTPUTS_PATH, 'stats')
    if OUTPUTS_PATH.exists():
        shutil.rmtree(OUTPUTS_PATH)
    OUTPUTS_PATH.mkdir()
    if not stats_path.exists():
        stats_path.mkdir()
    for experiment in range(experiments):
        if attribute and is_random_experiment and experiment > 0:
            config = randomizer.generate_new_param(attribute)
        elif is_random_experiment and experiment > 0:
            config = randomizer.generate_new()
        save_parameters_as_file(config, experiment=experiment)
        model = get_model(config)

        with Halo(text='Optimizing\n', spinner=Spinners.dots.value) as spinner:
            model.optimize()
            spinner.succeed('Optimized\n')
        
        if model.SolCount == 0:
            continue

        with Halo(text='Showing variables\n', spinner=Spinners.dots.value) as spinner:
            if not is_random_experiment:
                model.printAttr("X")
            if save:
                generate_tables(
                    model,
                    mappings=mappings,
                    save=save,
                    experiment=experiment
                )
            spinner.succeed('Printted all variables\n')

        if save:
            output_path = Path(output_path).absolute()
            model.write(str(output_path))
            save_plots(model, mappings, experiment=experiment)

            original = sys.stdout
            obj = model.getObjective()
            sys.stdout = Path(stats_path, f"model_stats_{experiment}.txt").open('w')
            print(f"Objetivo: {obj.getValue()}\n")
            model.printStats()
            sys.stdout = original
            model.printStats()
