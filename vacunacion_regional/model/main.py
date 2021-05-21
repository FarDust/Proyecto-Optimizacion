from random import seed

from gurobipy import GRB, Model, quicksum

from vacunacion_regional.model.parameters import ParametersConfig

__all__ = ["get_model"]

seed(10)

M = 1e12


def get_model(pm: ParametersConfig):
    model = Model("vacunacion-regional")

    # model.params.NonConvex = 2

    # add variables
    # var_name = model.addVars(*iterators, vtype=GRB.BINARY, name="<var_name>")
    # toma valor 1 si el camion camion se encuentra
    # en la comuna comuna en el dia dia

    # X_ncd: toma valor 1 si el camion n se encuentra en la comuna c en el día d.
    camion_en_comuna = model.addVars(
        pm.camiones,
        pm.comunas,
        pm.dias,
        vtype=GRB.BINARY,
        name="camion_n_en_comuna_c_dia_d",
    )
    # H_ncd: numero de vacunas en el camión camion en la comuna c en el dia d
    vacunas_camion_dia = model.addVars(
        pm.camiones, pm.comunas, pm.dias, vtype=GRB.INTEGER, name="vacunas_camion_dia"
    )
    # P_cd: numero de personas que se vacunaron en la comuna comuna en el dia dia
    personas_vacunadas_comuna_dia = model.addVars(
        pm.comunas, pm.dias, vtype=GRB.INTEGER, name="personas_vacunadas_comuna_dia"
    )
    # Y_cd: porcentaje de personas vacunadas en la comuna c hasta el dia d
    porcentajes_comuna_dia = model.addVars(
        pm.comunas, pm.dias, vtype=GRB.CONTINUOUS, name="porcentajes_comuna_dia"
    )

    # W_d: porcentaje promedio de personas vacunas entre todas las comunas el día d
    promedio_vacunacion = model.addVars(
        pm.dias, vtype=GRB.CONTINUOUS, name="promedio_vacunacion_dia"
    )

    model.update()

    # add restrictions
    #  model.addConstrs( generator, name="awesome_name")

    # R1: No se sobrepasa el presupuesto
    model.addConstrs(
        (
            quicksum(
                camion_en_comuna[camion, comuna, dia] * pm.costo_usar
                + (1 - camion_en_comuna[camion, comuna, dia]) * pm.costo_no_usar
                for comuna in pm.comunas
                for camion in pm.camiones
            )
            <= pm.fondos
            for dia in pm.dias
        ),
        name="R1",
    )

    # R2: Camión no lleva más vacunas que su capacidad máxima
    model.addConstrs(
        (
            vacunas_camion_dia[camion, comuna, dia] <= pm.capacidad_max
            for camion in pm.camiones
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R2",
    )

    # R3: Asignar un camión a una sola comuna y no a mas, en un mismo día
    model.addConstrs(
        (
            quicksum(camion_en_comuna[camion, comuna, dia] for comuna in pm.comunas)
            <= 1
            for camion in pm.camiones
            for dia in pm.dias
        ),
        name="R3",
    )

    # R4:  No se pueden utilizar más vacunas de las disponibles
    model.addConstr(
        quicksum(
            personas_vacunadas_comuna_dia[comuna, dia]
            for dia in pm.dias
            for comuna in pm.comunas
        )
        <= pm.vacunas_disponibles,
        name="R4",
    )

    # R5: En una comuna no se pueden vacunar más personas que el número de habitantes no vacunados
    model.addConstrs(
        (
            quicksum(personas_vacunadas_comuna_dia[comuna, dia] for dia in pm.dias)
            <= (pm.poblacion_objetivo[comuna] - pm.poblacion_vacunada[comuna])
            for comuna in pm.comunas
        ),
        name="R5",
    )

    # R6: Si un camión no se encuentra en una comuna, la cantidad de vacunas de ese camión en la comuna
    #     debe ser igual a cero.
    model.addConstrs(
        (
            M * camion_en_comuna[camion, comuna, dia]
            >= vacunas_camion_dia[camion, comuna, dia]
            for camion in pm.camiones
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R6",
    )

    # R7: En una comuna en un cierto día, no se pueden vacunar más personas que el número de vacunas en
    #     los camiones que se encuentran actualmente en la comuna.
    model.addConstrs(
        (
            personas_vacunadas_comuna_dia[comuna, dia]
            <= quicksum(
                vacunas_camion_dia[camion, comuna, dia] for camion in pm.camiones
            )
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R7",
    )

    # R8: En una comuna en un cierto día, no se pueden vacunar más personas que el límite de vacunación
    #     diario de los camiones en la comuna.
    model.addConstrs(
        (
            personas_vacunadas_comuna_dia[comuna, dia]
            <= quicksum(
                camion_en_comuna[camion, comuna, dia] * pm.vacunacion_dia
                for camion in pm.camiones
            )
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R8",
    )

    # R9: El porcentaje de personas vacunadas un cierto día depende del número de
    #     personas que han vacunado los camiones
    model.addConstrs(
        (
            pm.poblacion_objetivo[comuna] * porcentajes_comuna_dia[comuna, dia]
            == pm.poblacion_vacunada[comuna]
            + quicksum(personas_vacunadas_comuna_dia[comuna, rho] for rho in range(dia))
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R9",
    )

    # R10: Acota el valor del promedio entre los porcentajes de vacunación entre las comunas
    model.addConstrs(
        (
            len(pm.comunas) * promedio_vacunacion[dia]
            == quicksum(porcentajes_comuna_dia[comuna, dia] for comuna in pm.comunas)
            for dia in pm.dias
        ),
        name="R10",
    )

    # R11: En un día, una comuna no puede sobrepasar el promedio de vacunación (tal vez el dia siguiente)
    model.addConstrs(
        (
            porcentajes_comuna_dia[comuna, dia] <= promedio_vacunacion[dia]
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R11",
    )

    model.addConstrs(
        (
            porcentajes_comuna_dia[comuna, dia] <= 1
            for comuna in pm.comunas
            for dia in pm.dias
        ),
        name="R12",
    )

    obj = quicksum(
        personas_vacunadas_comuna_dia[comuna, dia] * (1 - pm.poblacion_vacunada[comuna] / pm.poblacion_objetivo[comuna])
        for comuna in pm.comunas
        for dia in pm.dias
    )

    model.setObjective(obj, GRB.MAXIMIZE)

    return model
