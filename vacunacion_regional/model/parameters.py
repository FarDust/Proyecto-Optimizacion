from dataclasses import dataclass
from random import randint, seed

__all__ = ['ParametersConfig']

seed(10)

ESTIMATED_MAX_VACCINATION_RATE_PER_TRUCK = 200

## SETS
# N: camiones disponibles
camiones = tuple(range(6))
# C: comunas
comunas = tuple(range(29))
# D: días
dias = tuple(range(5))

## PARAMS
# F: fondos disponibles
fondos = 1e6
# co_si: costo de utilizar un camión un día
costo_usar = 5e4
# co_no: costo de no utilizar un camión un día
costo_no_usar = 4e3

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
    ## SETS
    # N: camiones disponibles
    camiones: tuple = camiones
    # C: comunas
    comunas: tuple = comunas
    # D: días
    dias: tuple = dias

    ## PARAMS
    # F: fondos disponibles
    fondos: int = fondos
    # co_si: costo de utilizar un camión un día
    costo_usar: int = costo_usar
    # co_no: costo de no utilizar un camión un día
    costo_no_usar: int = costo_no_usar
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

