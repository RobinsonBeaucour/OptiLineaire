import gurobipy as gp
from itertools import product
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def division(a,b):
    if a == 0:
        return 0
    if b == 0:
        return 0
    return a/b

#####################################################################################
# Partie 1
#####################################################################################

# 1.1 ###############################################################################

class Centrale:
    def __init__(self, name, N, Pmin, Pmax, Cmwh):
        self.name = name
        self.N = N
        self.Pmin = Pmin
        self.Pmax = Pmax
        self.Cmwh = Cmwh

def variable_decision_thermique(model,dict_Thermique):
    dict_N = {}
    dict_P = {}
    for t in range(24):
        for X in dict_Thermique:
            dict_N[X,t] = model.addVar(lb=0,ub=dict_Thermique[X].N,vtype=gp.GRB.INTEGER,name=f"Nombre de centrale {X} allumées à {t}h")
        for X in dict_Thermique:
            dict_P[X,t] = model.addVar(name=f"Puissance totale {X} à {t}h")
    return dict_N, dict_P

def contraintes_puissance_thermique(model,dict_N,dict_P,dict_Thermique):
    for t in range(24):
        for X in dict_Thermique:
            model.addConstr(dict_P[X,t]<=dict_N[X,t] * dict_Thermique[X].Pmax, name=f"borne sup puissance, {X} à {t}h")
            model.addConstr(dict_P[X,t]>=dict_N[X,t] * dict_Thermique[X].Pmin, name=f"borne inf puissance, {X} à {t}h")

def contraintes_equilibre(model,dict_P,dict_Thermique,consommation):
    for t in range(24):
        model.addConstr(gp.quicksum([dict_P[X,t] for X in dict_Thermique])==consommation[t])

#####################################################################################
# Partie 2
#####################################################################################

# 2.1 ###############################################################################

class Centrale2:
    def __init__(self, name, N, Pmin, Pmax, Cstart, Cbase, Cmwh):
        self.name = name
        self.N = N
        self.Pmin = Pmin
        self.Pmax = Pmax
        self.Cstart = Cstart
        self.Cbase = Cbase
        self.Cmwh = Cmwh

# 2.2 ###############################################################################

def variable_decision_thermique_avec_demarrage(model,dict_Thermique):
    dict_N, dict_P = variable_decision_thermique(model,dict_Thermique)
    dict_Nstart = {}
    for X in dict_Thermique:
        for t in range(24):
            dict_Nstart[X,t] = model.addVar(lb=0,ub=dict_Thermique[X].N,vtype=gp.GRB.INTEGER,name=f"Nombre de centrale {X} démarrées à {t}h")
    return dict_N, dict_Nstart, dict_P

def contraintes_demarrage(model,dict_N,dict_Nstart,dict_Thermique,cyclique=True):
    heure = np.arange(24)
    for t in range(24):
        for X in dict_Thermique:
            if cyclique:
                model.addConstr(dict_Nstart[X,t]<=dict_Thermique[X].N-dict_N[X,heure[t-1]], name = f"Nombre max de centrale {X} démarable à {t}")
                model.addConstr(dict_N[X,t]<=dict_Nstart[X,t]+dict_N[X,heure[t-1]], name = f"Nombre max de centrale {X} en fonctionnement à {t}")
            else:
                if t ==0:
                    model.addConstr(dict_Nstart[X,t]<= dict_Thermique[X].N, name = f"Nombre max de centrale {X} démarable à {t}")
                    model.addConstr(dict_N[X,t] <= dict_Nstart[X,t], name = f"Nombre max de centrale {X} en fonctionnement à {t}")
                else:
                    model.addConstr(dict_Nstart[X,t]<= dict_Thermique[X].N - dict_N[X,t-1], name = f"Nombre max de centrale {X} démarable à {t}")
                    model.addConstr(dict_N[X,t] <= dict_Nstart[X,t] + dict_N[X,t-1], name = f"Nombre max de centrale {X} en fonctionnement à {t}")

#####################################################################################
# Partie 3
#####################################################################################

def contraintes_reserve_de_puissance(model,dict_N,dict_Thermique,consommation):
    for t in range(24):
        model.addConstr(gp.quicksum([dict_N[X,t]*dict_Thermique[X].Pmax for X in dict_Thermique])>= 1.15 * consommation[t], name = f"Réserve de puissance à {t}")

#####################################################################################
# Partie 5
#####################################################################################

class Centrale_hydro:
    def __init__(self, name, P, Cstart, Cheure, debit):
        self.name = name
        self.P = P
        self.Cstart = Cstart
        self.Cheure = Cheure
        self.debit = debit

def variable_decision_hydraulique(model,dict_Hydro):
    dict_H = {}
    dict_Hstart = {}
    for Y in dict_Hydro:
        for t in range(24):
            dict_H[Y,t] = model.addVar(vtype=gp.GRB.BINARY, name = f"Centrale Hydro {Y} fonctionne à l'heure {t}")
            dict_Hstart[Y,t] = model.addVar(vtype=gp.GRB.BINARY, name = f"Centrale Hydro {Y} démarre à l'heure {t}")

        return dict_H, dict_Hstart

