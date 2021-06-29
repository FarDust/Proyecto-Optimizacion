from dataclasses import dataclass
from random import randint, seed
import random
import numpy as np
from numpy.random import uniform
from typing import Dict, Tuple

__all__ = ['ParametersConfig']

seed(10)

ESTIMATED_MAX_VACCINATION_RATE_PER_TRUCK = 400
# SETS
# N: camiones disponibles
camiones = tuple(range(6))
# C: comunas
comunas = tuple(range(29))
# D: días
dias = tuple(range(100))

# PARAMS
# F: fondos disponibles
# fondos = 1e6
# # co_si: costo de utilizar un camión un día
# costo_usar = 5e4
# # co_no: costo de no utilizar un camión un día
# costo_no_usar = 4e3

# ho_c: habitantes objetivo comuna c
poblacion_objetivo = tuple([
    randint(100, 5000) for comuna in comunas
])
# hv_c: habitantes vacunados comuna c
poblacion_vacunada = tuple([
    randint(100, poblacion_objetivo[comuna]) for comuna in comunas
])
# v: capacidad de vacunación por día de un centro móvil
vacunacion_dia = ESTIMATED_MAX_VACCINATION_RATE_PER_TRUCK
# H_max: capacidad de vacunas en camión
capacidad_max = 1e3
# V: vacunas disponibles
vacunas_disponibles = 5e5


@dataclass
class ParametersConfig():
    # SETS
    # N: camiones disponibles
    camiones: tuple = camiones
    # C: comunas
    comunas: tuple = comunas
    # D: días
    dias: tuple = dias

    # PARAMS
    # F: fondos disponibles
    #fondos: int = fondos
    # co_si: costo de utilizar un camión un día
    #costo_usar: int = costo_usar
    # co_no: costo de no utilizar un camión un día
    #costo_no_usar: int = costo_no_usar
    # ho_c: habitantes objetivo comuna c
    poblacion_objetivo: tuple = poblacion_objetivo
    # hv_c: habitantes vacunados comuna c
    poblacion_vacunada: tuple = poblacion_vacunada
    # v: capacidad de vacunación por día de un centro móvil
    vacunacion_dia: int = vacunacion_dia
    # H_max: capacidad de vacunas en camión
    capacidad_max: int = capacidad_max
    # V: vacunas disponibles
    vacunas_disponibles: int = vacunas_disponibles


class parametersRandomizer(object):

    def __init__(
        self,
        parameters: ParametersConfig
    ) -> None:
        super().__init__()
        self.parameters = parameters

    def generate_new(self) -> ParametersConfig:
        multipliers = {
            'camiones': random.uniform(0, 2),
            'dias': random.uniform(0.75, 1.15),
            'poblacion_objetivo': uniform(0.5, 2, len(self.parameters.comunas)),
            'poblacion_vacunada': uniform(0.5, 2, len(self.parameters.comunas)),
            'vacunacion_dia': random.uniform(0.5, 2),
            'capacidad_max': random.uniform(0.5, 2),
            'vacunas_disponibles': random.uniform(0.5, 2),
        }

        poblacion_objetivo = np.multiply(np.array(
            self.parameters.poblacion_objetivo), multipliers['poblacion_objetivo']).astype(int)
        poblacion_objetivo[poblacion_objetivo <= 1] = 1

        poblacion_vacunada = np.multiply(np.array(
            self.parameters.poblacion_vacunada), multipliers['poblacion_vacunada']).astype(int)
        poblacion_vacunada[poblacion_vacunada >
                           poblacion_objetivo.max()] = poblacion_objetivo.max()

        new_parameters = ParametersConfig(
            comunas=self.parameters.comunas,
            camiones=tuple(
                range(max(1, int(len(self.parameters.camiones) * multipliers['camiones'])))),
            dias=tuple(
                range(max(1, int(len(self.parameters.dias) * multipliers['dias'])))),
            poblacion_objetivo=tuple(map(int, poblacion_objetivo)),
            poblacion_vacunada=tuple(map(int, poblacion_vacunada)),
            vacunacion_dia=max(
                1, int(self.parameters.vacunacion_dia * multipliers['vacunacion_dia'])),
            capacidad_max=max(
                1, int(self.parameters.capacidad_max * multipliers['capacidad_max'])),
            vacunas_disponibles=max(
                1, int(self.parameters.capacidad_max * multipliers['vacunas_disponibles']))
        )
        return new_parameters
