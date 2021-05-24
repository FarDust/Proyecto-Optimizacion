from abc import ABC, abstractmethod
from typing import Dict, List
from gurobipy import Model

import pandas as pd
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


parsing_chain = PersonasVacunadasComunaDiaParser(
    PromedioVacunacionDiaParser(
        PorcentajesComunaDiaParser(
            NullParser()
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
