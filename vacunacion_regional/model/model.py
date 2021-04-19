from random import seed

from gurobipy import quicksum
from gurobipy import Model, GRB

#from vacunacion_regional.model.parameters import *
from parameters import *

__all__ = ["get_model"]

seed(10)


def get_model():
    m = Model("vacunacion-regional")

    # add variables
    # var_name = m.addVars( *iterators, vtype=GRB.BINARY, name="<var_name>")
    x = m.addVars(N, C, D, vtype=GRB.BINARY,      name="x")     # toma valor 1 si el camion n se encuentra en la comuna c en el dia d
    h = m.addVars(N, D,    vtype=GRB.INTEGER,     name="h")     # numero de vacunas en el cami ́on n en el dia d
    p = m.addVars(C, D,    vtype=GRB.INTEGER,     name="p")     # numero de personas que se vacunaron en la comuna c en el dia d
    y = m.addVars(C, D,    vtype=GRB.CONTINUOUS,  name="y")     # porcentaje de personas vacunadas en la comuna c hasta el dia d

    m.update()

    # add restrictions
    #  m.addConstrs( generator, name="awesome_name")
    m.addConstrs((quicksum(x[n, c, d] * c_v + (1 - x[n, c, d]) * c_vn for c in C for n in N) <= F for d in D),  name="R1")
    m.addConstrs((h[n, d] <= H_max for n in N for d in D),                                                      name="R2")
    m.addConstrs((quicksum(x[n, c, d] for c in C) <= 1 for n in N for d in D),                                  name="R3")
    m.addConstr(quicksum(p[c, d] for d in D for c in C) <= V_t,                                                 name="R4")
    m.addConstrs((quicksum(p[c, d] for d in D) <= ha[c] - p_v[c] for c in C),                                   name="R5")
    m.addConstrs((p[c, d] <= quicksum(x[n, c, d] * h[n, d] for n in N) for c in C for d in D),                  name="R6")
    m.addConstrs((p[c, d] <= v for c in C for d in D),                                                          name="R7")
    m.addConstrs((ha[c] * y[c, d] == p_v[c] + quicksum(p[c, rho] for rho in range(d)) for c in C for d in D),   name="R8")


    # define objective function
    obj = quicksum(p[c, d] * (1 - y[c, d]) for c in C for d in D)
    m.setObjective(obj, GRB.MAXIMIZE)

    return m


if __name__ == "__main__":
    m = get_model()

    m.optimize()

    m.printAttr("X")