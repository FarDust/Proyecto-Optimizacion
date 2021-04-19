#from vaccines import data                      # Para probar el modelo con datos reales
from random import randint, seed                # Para probar el modelo con datos random


seed(10)


# SETS
N = range(10)                                             # Camiones disponibles
C = range(303)                                            # Comunas
D = range(30)                                             # Días

# PARAMS
F     = 100000000                                          # Fondos disponibles
c_v   = 50                                                 # Costo variable de utilizar un camión
c_vn  = 10                                                 # Costo variable de no utilizar un camión
v     = 1000                                               # Capacidad de vacunación por día centro móvil
ha    = {c: randint(10000, 500000) for c in C}             # Habitantes objetivo comuna c
p_v   = {c: randint(1000, ha[c]) for c in C}               # Habitantes vacunados comuna c
H_max = 10000                                              # Capacidad de vacunas en camión
V_t   = 10000000                                           # Vacunas disponibles