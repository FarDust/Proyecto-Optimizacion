from random import seed

from gurobipy import GRB, Model, quicksum

from vacunacion_regional.model.parameters import ParametersConfig

__all__ = ["get_model"]

seed(10)

M = 10e6


def get_model(pm: ParametersConfig):
    model = Model("vacunacion-regional")

    # model.params.NonConvex = 2

    # add variables
    # var_name = model.addVars(*iterators, vtype=GRB.BINARY, name="<var_name>")
    # toma valor 1 si el camion camion se encuentra
    # en la comuna comuna en el dia dia
    # X
    camion_en_comuna = model.addVars(
        pm.camiones, pm.comunas, pm.dias, vtype=GRB.BINARY,
        name="camion_en_comuna"
    )
    # numero de vacunas en el camión camion en el dia dia
    vacunas_camion_dia = model.addVars(
        pm.camiones, pm.dias, vtype=GRB.INTEGER,
        name="vacunas_camion_dia"
    )
    # numero de personas que se vacunaron en la comuna comuna en el dia dia
    personas_vacunadas_comuna_dia = model.addVars(
        pm.comunas, pm.dias, vtype=GRB.INTEGER,
        name="personas_vacunadas_comuna_dia"
    )

    model.update()

    # add restrictions
    #  model.addConstrs( generator, name="awesome_name")
    model.addConstrs(
        (
            quicksum(
                camion_en_comuna[camion, comuna, dia] * pm.costo_usar
                + (1 - camion_en_comuna[camion, comuna, dia])
                * pm.costo_no_usar
                for comuna in pm.comunas
                for camion in pm.camiones
            )
            <= pm.fondos
            for dia in pm.dias
        ),
        name="R1",
    )
    model.addConstrs(
        (
            vacunas_camion_dia[camion, dia] <= pm.capacidad_max
            for camion in pm.camiones
            for dia in pm.dias
        ),
        name="R2",
    )
    model.addConstrs(
        (
            quicksum(
                camion_en_comuna[camion, comuna, dia] for comuna in pm.comunas
                )
            <= 1
            for camion in pm.camiones
            for dia in pm.dias
        ),
        name="R3",
    )
    model.addConstr(
        quicksum(
            personas_vacunadas_comuna_dia[comuna, dia]
            for dia in pm.dias
            for comuna in pm.comunas
        )
        <= pm.vacunas_disponibles,
        name="R4",
    )
    model.addConstrs(
        (
            quicksum(
                personas_vacunadas_comuna_dia[comuna, dia] for dia in pm.dias
            )
            <= (pm.poblacion_objetivo[comuna] - pm.poblacion_vacunada[comuna])
            for comuna in pm.comunas
        ),
        name="R5",
    )
    model.addConstrs(
        (
            personas_vacunadas_comuna_dia[comuna, dia]
            <= quicksum(
                camion_en_comuna[camion, comuna, dia]
                * vacunas_camion_dia[camion, dia]
                for camion in pm.camiones
            )
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R6",
    )
    model.addConstrs(
        (
            personas_vacunadas_comuna_dia[comuna, dia] <= quicksum(
                camion_en_comuna[camion, comuna, dia] * pm.vacunacion_dia
                for camion in pm.camiones
            )
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R7",
    )
    # model.addConstrs(
    #     (
    #         pm.poblacion_objetivo[comuna] *
    #         porcentajes_comuna_dia[comuna, dia]
    #         == pm.poblacion_vacunada[comuna]
    #         + quicksum(
    #             personas_vacunadas_comuna_dia[comuna, rho]
    #             for rho in range(dia)
    #             )
    #         for comuna in pm.comunas
    #         for dia in pm.dias
    #     ),
    #     name="R8",
    # )

    # define objective function
    # # OPT1: versión no lineal
    # obj = quicksum(
    #   p[comuna, dia] * (1 - y[comuna, dia])
    #   for comuna in comunas
    #   for dia in dias
    # )
    # # OPT2: versión lineal
    obj = quicksum(
        personas_vacunadas_comuna_dia[comuna, dia]
        * (1 - (pm.poblacion_vacunada[comuna] / pm.poblacion_objetivo[comuna]))
        for comuna in pm.comunas
        for dia in pm.dias
    )

    model.setObjective(obj, GRB.MAXIMIZE)

    return model
