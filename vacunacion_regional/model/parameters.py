# from vaccines import data
# Para probar el modelo con datos reales
# Para probar el modelo con datos random
from random import randint, seed

seed(10)


# SETS
camiones = range(5)  # Camiones disponibles
comunas = range(29)  # Comunas
dias = range(20)  # Días

# PARAMS
fondos = 100000000  # Fondos disponibles
# Costo variable de utilizar un camión
costo_usar = 50
# Costo variable de no utilizar un camión
costo_no_usar = 4
# Capacidad de vacunación por día centro móvil
vacunacion_dia = 1000
poblacion_objetivo = {
    comuna: randint(10000, 500000) for comuna in comunas
}  # Habitantes objetivo comuna comuna
# Habitantes vacunados comuna comuna
poblacion_vacunada = {
    comuna: randint(1000, poblacion_objetivo[comuna]) for comuna in comunas
}
# Capacidad de vacunas en camión
capacidad_max = 10000
vacunas_disponibles = 10000000  # Vacunas disponibles
