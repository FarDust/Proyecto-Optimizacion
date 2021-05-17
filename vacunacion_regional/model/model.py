from random import seed

from gurobipy import GRB, Model, quicksum

import vacunacion_regional.model.parameters as pm

__all__ = ["get_model"]

seed(10)

M = 10e6


def get_model():
    model = Model("vacunacion-regional")

    # model.params.NonConvex = 2

    # add variables
    # var_name = model.addVars(*iterators, vtype=GRB.BINARY, name="<var_name>")
    # toma valor 1 si el camion n se encuentra en la comuna c en el dia d
    # X
    camion_en_comuna = model.addVars(
        pm.camiones, pm.comunas, pm.dias, vtype=GRB.BINARY,
        name="camion_en_comuna"
    )
    # numero de vacunas en el camión n en el dia d
    vacunas_camion_dia = model.addVars(
        pm.camiones, pm.dias, vtype=GRB.INTEGER,
        name="vacunas_camion_dia"
    )
    # numero de personas que se vacunaron en la comuna c en el dia d
    personas_vacunadas_comuna_dia = model.addVars(
        pm.comunas, pm.dias, vtype=GRB.INTEGER,
        name="personas_vacunadas_comuna_dia"
    )
    # porcentaje de personas vacunadas en la comuna c hasta el dia d
    porcentajes_comuna_dia = model.addVars(
        pm.comunas, pm.dias, vtype=GRB.CONTINUOUS,
        name="porcentajes_comuna_dia"
    )

    model.update()

    # add restrictions
    #  model.addConstrs( generator, name="awesome_name")
    model.addConstrs(
        (
            quicksum(
                camion_en_comuna[n, c, d] * pm.costo_usar
                + (1 - camion_en_comuna[n, c, d]) * pm.costo_no_usar
                for c in pm.comunas
                for n in pm.camiones
            )
            <= pm.fondos
            for d in pm.dias
        ),
        name="R1",
    )
    model.addConstrs(
        (
            vacunas_camion_dia[n, d] <= pm.capacidad_max
            for n in pm.camiones
            for d in pm.dias
        ),
        name="R2",
    )
    model.addConstrs(
        (
            quicksum(camion_en_comuna[n, c, d] for c in pm.comunas) <= 1
            for n in pm.camiones
            for d in pm.dias
        ),
        name="R3",
    )
    model.addConstr(
        quicksum(
            personas_vacunadas_comuna_dia[c, d] for d in pm.dias
            for c in pm.comunas
        )
        <= pm.vacunas_disponibles,
        name="R4",
    )
    model.addConstrs(
        (
            quicksum(personas_vacunadas_comuna_dia[c, d] for d in pm.dias)
            <= pm.poblacion_objetivo[c] - pm.poblacion_vacunada[c]
            for c in pm.comunas
        ),
        name="R5",
    )
    model.addConstrs(
        (
            personas_vacunadas_comuna_dia[c, d]
            <= quicksum(vacunas_camion_dia[n, d] for n in pm.camiones)
            for c in pm.comunas
            for d in pm.dias
        ),
        name="R6",
    )
    model.addConstrs(
        (
            personas_vacunadas_comuna_dia[c, d]
            <= M * quicksum(camion_en_comuna[n, c, d] for n in pm.camiones)
            for c in pm.comunas
            for d in pm.dias
        ),
        name="R7",
    )
    model.addConstrs(
        (
            personas_vacunadas_comuna_dia[c, d] <= pm.vacunacion_dia
            for c in pm.comunas
            for d in pm.dias
        ),
        name="R8",
    )
    model.addConstrs(
        (
            pm.poblacion_objetivo[c] * porcentajes_comuna_dia[c, d]
            == pm.poblacion_vacunada[c]
            + quicksum(
                personas_vacunadas_comuna_dia[c, rho] for rho in range(d)
                )
            for c in pm.comunas
            for d in pm.dias
        ),
        name="R9",
    )

    # define objective function
    # # OPT1: versión no lineal
    # obj = quicksum(
    #   p[comuna, dia] * (1 - y[comuna, dia])
    #   for comuna in comunas
    #   for dia in dias
    # )
    # # OPT2: versión lineal
    obj = quicksum(
        personas_vacunadas_comuna_dia[c, d]
        * (1 - (pm.poblacion_vacunada[c] / pm.poblacion_objetivo[c]))
        for c in pm.comunas
        for d in pm.dias
    )

    model.setObjective(obj, GRB.MAXIMIZE)

    return model


if __name__ == "__main__":
    model = get_model()

    model.optimize()

    model.printAttr("X")

    model.printStats()
