# from vaccines import data
# Para probar el modelo con datos reales
# Para probar el modelo con datos random
from random import randint, seed
from dataclasses import dataclass

__all__ = ['ParametersConfig']

seed(10)

ESTIMATED_MAX_VACCINATION_RATE_PER_COMUNA = 1200

# SETS
camiones = tuple(range(5))  # Camiones disponibles
comunas = tuple(range(29))  # Comunas
dias = tuple(range(35))  # Días

# PARAMS
fondos = 1e6  # Fondos disponibles
# Costo variable de utilizar un camión
costo_usar = 5e4
# Costo variable de no utilizar un camión
costo_no_usar = 4e3
# Capacidad de vacunación por día centro móvil
vacunacion_dia = ESTIMATED_MAX_VACCINATION_RATE_PER_COMUNA // len(camiones)
poblacion_objetivo = tuple([
    randint(100, 5000) for comuna in comunas
  ])  # Habitantes objetivo comuna comuna
# Habitantes vacunados comuna comuna
poblacion_vacunada = tuple([
    randint(100, poblacion_objetivo[comuna]) for comuna in comunas
])
# Capacidad de vacunas en camión
capacidad_max = 1e3
vacunas_disponibles = 5e5  # Vacunas disponibles


@dataclass
class ParametersConfig():
    # SETS
    camiones: tuple = camiones  # Camiones disponibles
    comunas: tuple = comunas  # Comunas
    dias: tuple = dias  # Días

    # PARAMS
    fondos: int = fondos  # Fondos disponibles
    # Costo variable de utilizar un camión
    costo_usar: int = costo_usar
    # Costo variable de no utilizar un camión
    costo_no_usar: int = costo_no_usar
    # Capacidad de vacunación por día centro móvil
    vacunacion_dia: int = vacunacion_dia
    # Habitantes objetivo comuna comuna
    poblacion_objetivo: tuple = poblacion_objetivo
    # Habitantes vacunados comuna comuna
    poblacion_vacunada: tuple = poblacion_vacunada
    # Capacidad de vacunas en camión
    capacidad_max: int = capacidad_max
    vacunas_disponibles: int = vacunas_disponibles  # Vacunas disponibles

