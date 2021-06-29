from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List
from vacunacion_regional.setting import OUTPUTS_PATH, ROOT_DIR
from gurobipy import Model

import pandas as pd
from pandas.core.frame import DataFrame
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style="darkgrid")


class VariableParser(ABC):

    def __init__(self, next_parser: "VariableParser" = None) -> None:
        super().__init__()
        if next_parser:
            self.next_parser = next_parser

    @abstractmethod
    def parse(self, name: str, indexes: List[int], value: float) -> Dict:
        pass


class NullParser(VariableParser):

    def parse(self, name: str, indexes: List[int], value: float) -> Dict:
        return dict()


# porcentajes_comuna_dia
class PorcentajesComunaDiaParser(VariableParser):

    def parse(self, name: str, indexes: List[int], value: float) -> Dict:
        if "porcentajes_comuna_dia" in name:
            comuna, dia = indexes
            return {
                "dia": int(dia),
                "comuna": int(comuna),
                "value": value
            }
        else:
            return self.next_parser.parse(name, indexes, value)


# promedio_vacunacion_dia
class PromedioVacunacionDiaParser(VariableParser):

    def parse(self, name: str, indexes: List[int], value: float) -> Dict:
        if "promedio_vacunacion_dia" in name:
            dia = indexes[0]
            return {
                "dia": int(dia),
                "value": value
            }
        else:
            return self.next_parser.parse(name, indexes, value)


# personas_vacunadas_comuna_dia
class PersonasVacunadasComunaDiaParser(VariableParser):

    def parse(self, name: str, indexes: List[int], value: float) -> Dict:
        if "personas_vacunadas_comuna_dia" in name:
            comuna, dia = indexes
            return {
                "dia": int(dia),
                "comuna": int(comuna),
                "value": value
            }
        else:
            return self.next_parser.parse(name, indexes, value)  


# camion_n_en_comuna_c_dia_d
class CamionComunaDiaParser(VariableParser):

    def parse(self, name: str, indexes: List[int], value: float) -> Dict:
        if "camion_n_en_comuna_c_dia_d" in name:
            camion, comuna, dia = indexes
            return {
                "camion": int(camion),
                "dia": int(dia),
                "comuna": int(comuna),
                "value": value
            }
        else:
            return self.next_parser.parse(name, indexes, value)   


# vacunas_camion_dia
class VacunasCamionDiaParser(VariableParser):

    def parse(self, name: str, indexes: List[int], value: float) -> Dict:
        if "vacunas_camion_dia" in name:
            camion, comuna, dia = indexes
            return {
                "camion": int(camion),
                "comuna": int(comuna),
                "dia": int(dia),
                "value": value
            }
        else:
            return self.next_parser.parse(name, indexes, value)   


# comuna_critica
class ComunaCriticaParser(VariableParser):

    def parse(self, name: str, indexes: List[int], value: float) -> Dict:
        if "comuna_critica" in name:
            comuna, dia = indexes
            return {
                "comuna": int(comuna),
                "dia": int(dia),
                "value": value
            }
        else:
            return self.next_parser.parse(name, indexes, value)   


parsing_chain = PersonasVacunadasComunaDiaParser(
    PromedioVacunacionDiaParser(
        PorcentajesComunaDiaParser(
            CamionComunaDiaParser(
                VacunasCamionDiaParser(
                    ComunaCriticaParser(
                        NullParser()
                    )
                )
            )
        )
    )
)


def get_mapped_variables(model: Model):
    model_variables = model.getVars()
    mapped_variables = {
        variable.VarName: variable.x for variable in model_variables
        }
    return mapped_variables


def process_model_variables(variables: dict) -> Dict:
    final_mappings = dict()
    for variable_name, value in variables.items():
        name, indexes = variable_name.strip(']').split('[')
        indexes = tuple(map(lambda x: float(x), indexes.split(',')))
        parsed = parse_variable(name, indexes, value)
        if parsed != dict():
            if not(name in final_mappings.keys()):
                final_mappings[name] = list()
            final_mappings[name].append(parsed)
    return final_mappings


def parse_variable(name: str, indexes: List[int], value: float) -> Dict:
    """
    {
        column1: value1
        column2: value2
    }
    """
    return parsing_chain.parse(name, indexes, value)


def get_porcentajes_vacunacion_plot(variables: Dict, mappings: Dict):
    data = pd.json_normalize(variables['porcentajes_comuna_dia'])
    data['comuna'] = data['comuna'].map(mappings['comunas'])
    plot = sns.lineplot(
        data=data,
        x="dia",
        y="value",
        hue="comuna",
        markers=True,
        style="comuna"
        )
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    return plot


def get_porcentajes_vacunacion_target_plot(variables: Dict, mappings: Dict):
    data = pd.json_normalize(variables['porcentajes_comuna_dia'])
    data['comuna'] = data['comuna'].map(mappings['comunas'])
    plot = sns.lineplot(data=data, x="dia", y="value")
    return plot


def generate_tables(model: Model, mappings=None, save=False, experiment=1) ->Dict[str, DataFrame]:
    mapped_variables = get_mapped_variables(model)
    variables = process_model_variables(mapped_variables)
    tables = dict()
    for variable_key in variables.keys():
        table = pd.json_normalize(variables[variable_key])
        if mappings is not None and 'comuna' in table.columns:
            table['comuna'] = table['comuna'].map(mappings['comunas'])
        if save:
            csv_path = Path(OUTPUTS_PATH, 'tables')
            if not csv_path.exists():
                csv_path.mkdir()
            table.to_csv(str(Path(csv_path, f"{variable_key}_{experiment}.csv")))
        tables[variable_key] = table.copy()
    return tables
