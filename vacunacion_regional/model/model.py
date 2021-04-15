from random import seed

from gurobipy import quicksum
from gurobipy import Model, GRB

from vacunacion_regional.model.parameters import *

__all__ = ["get_model"]

seed(10)


def get_model():
    model = Model("vacunacion-regional")

    # add variables
    # var_name = model.addVars( *iterators, vtype=GRB.BINARY, name="<var_name>")

    model.update()

    # add restrictions
    #  model.addConstrs( generator, name="awesome_name")

    obj = None

    model.setObjective(obj, GRB.MINIMIZE)
    return model
