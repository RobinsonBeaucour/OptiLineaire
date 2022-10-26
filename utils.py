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
    '''
    Class permettant de regrouper les informations sur un type de centrale pour faciliter
    l'implementation du code
    '''
    def __init__(self, name, N, Pmin, Pmax, Cmwh):
        self.name = name
        self.N = N
        self.Pmin = Pmin
        self.Pmax = Pmax
        self.Cmwh = Cmwh

def variable_decision_thermique(model,dict_Thermique):
    '''
    Fontion générant les variables de décision
    Output :
    dict_N[X,t] dictionnaire contenant les variables de décision associées au nombre de centrale X en fonctionnement à l'instant t
    dict_P[X,t] dictionnaire contenant les variables de décision sur la puissance total des centrales X à l'instant t
    '''
    dict_N = {}
    dict_P = {}
    for t in range(24):
        for X in dict_Thermique:
            dict_N[X,t] = model.addVar(lb=0,ub=dict_Thermique[X].N,vtype=gp.GRB.INTEGER,name=f"Nombre de centrale {X} allumées à {t}h")
            dict_P[X,t] = model.addVar(name=f"Puissance totale {X} à {t}h")
    return dict_N, dict_P

def contraintes_puissance_thermique(model,dict_N,dict_P,dict_Thermique):
    '''
    Ajoute au modèle les contraintes de puissance que les centrales peuvent atteindre.
    Les centrales allumées doivent avoir une puissance entre Pmin et Pmax
    '''
    for t in range(24):
        for X in dict_Thermique:
            model.addConstr(dict_P[X,t]<=dict_N[X,t] * dict_Thermique[X].Pmax, name=f"borne sup puissance, {X} à {t}h")
            model.addConstr(dict_P[X,t]>=dict_N[X,t] * dict_Thermique[X].Pmin, name=f"borne inf puissance, {X} à {t}h")

def contraintes_equilibre(model,dict_P,dict_Thermique,consommation):
    '''
    Ajoute au modèle la contraite d'équilibre offre-demande
    '''
    for t in range(24):
        model.addConstr(gp.quicksum([dict_P[X,t] for X in dict_Thermique])==consommation[t])

#####################################################################################
# Partie 2
#####################################################################################

# 2.1 ###############################################################################

class Centrale2:
    '''
    Class permettant de regrouper les informations sur un type de centrale pour faciliter
    l'implementation du code
    '''
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
    '''
    Fontion générant les variables de décision
    Output :
    dict_N[X,t] dictionnaire contenant les variables de décision associées au nombre de centrale X en fonctionnement à l'instant t
    dict_P[X,t] dictionnaire contenant les variables de décision sur la puissance total des centrales X à l'instant t
    dict_Nstart[X,t] dictionnaire contenant les variables de décision sur le nombre de centrales X démarrées à l'instant t
    '''
    dict_N, dict_P = variable_decision_thermique(model,dict_Thermique)
    dict_Nstart = {}
    for X in dict_Thermique:
        for t in range(24):
            dict_Nstart[X,t] = model.addVar(lb=0,ub=dict_Thermique[X].N,vtype=gp.GRB.INTEGER,name=f"Nombre de centrale {X} démarrées à {t}h")
    return dict_N, dict_Nstart, dict_P

def contraintes_demarrage(model,dict_N,dict_Nstart,dict_Thermique,cyclique=True):
    '''
    Ajoute au modèle les contraintes sur le démarrage des centrales
    '''
    heure = np.arange(24)
    for t in range(24):
        for X in dict_Thermique:
            if cyclique:
                # 2.2.2
                model.addConstr(dict_Nstart[X,t]<=dict_Thermique[X].N-dict_N[X,heure[t-1]], name = f"Nombre max de centrale {X} démarable à {t}")
                # 2.2.1
                model.addConstr(dict_N[X,t]<=dict_Nstart[X,t]+dict_N[X,heure[t-1]], name = f"Nombre max de centrale {X} en fonctionnement à {t}")
            else:
                if t ==0:
                    # 2.2.2
                    model.addConstr(dict_Nstart[X,t]<= dict_Thermique[X].N, name = f"Nombre max de centrale {X} démarable à {t}")
                    # 2.2.1
                    model.addConstr(dict_N[X,t] <= dict_Nstart[X,t], name = f"Nombre max de centrale {X} en fonctionnement à {t}")
                else:
                    # 2.2.2
                    model.addConstr(dict_Nstart[X,t]<= dict_Thermique[X].N - dict_N[X,t-1], name = f"Nombre max de centrale {X} démarable à {t}")
                    # 2.2.1
                    model.addConstr(dict_N[X,t] <= dict_Nstart[X,t] + dict_N[X,t-1], name = f"Nombre max de centrale {X} en fonctionnement à {t}")

#####################################################################################
# Partie 3
#####################################################################################

def contraintes_reserve_de_puissance(model,dict_N,dict_Thermique,consommation):
    '''
    Ajoute au modèle la contrainte de réserve de puissance de 15% par rapport à la demande
    '''
    for t in range(24):
        model.addConstr(gp.quicksum([dict_N[X,t]*dict_Thermique[X].Pmax for X in dict_Thermique])>= 1.15 * consommation[t], name = f"Réserve de puissance à {t}")

#####################################################################################
# Partie 5
#####################################################################################

# 5.1 ###############################################################################

class Centrale_hydro:
    '''
    Class permettant de regrouper les informations sur un type de centrale pour faciliter
    l'implementation du code
    '''
    def __init__(self, name, P, Cstart, Cheure, debit):
        self.name = name
        self.P = P
        self.Cstart = Cstart
        self.Cheure = Cheure
        self.debit = debit

def variable_decision_hydraulique(model,dict_Hydro):
    '''
    Génère les variables de décision du problème liées à l'hydraulique
    output :
    dict_H[Y,t] dictionnaire contenant les VD sur le fonctionnement de la centrale Y à l'instant t
    dict_Hstart[Y,t] dictionnaire contenant les VD sur le démarrage des centrales Y à l'instant t
    '''
    dict_H = {}
    dict_Hstart = {}
    for Y in dict_Hydro:
        for t in range(24):
            dict_H[Y,t] = model.addVar(vtype=gp.GRB.BINARY, name = f"Centrale Hydro {Y} fonctionne à l'heure {t}")
            dict_Hstart[Y,t] = model.addVar(vtype=gp.GRB.BINARY, name = f"Centrale Hydro {Y} démarre à l'heure {t}")

    return dict_H, dict_Hstart

def contraintes_hydraulique(model,dict_Hstart,dict_H,dict_Hydro):
    '''
    Ajoute les contraintes de démarrage de l'hydraulique (5.1.2)
    '''
    heure = np.arange(24)
    for t in range(24):
        for Y in dict_Hydro:
            # model.addConstr(dict_Hstart[Y,t]<=dict_H[Y,t], name = f"Le nombre de centrale {Y} en fonctionnement supérieur au nombre démarré à {t}")
            model.addConstr(dict_H[Y,t] <= dict_Hstart[Y,t] + dict_H[Y,heure[t-1]], name = f"Contrainte centrale {Y} fonctionnant à {t}")

def contraintes_equilibre_avec_hydro(model,dict_H,dict_P,dict_Thermique,dict_Hydro,consommation):
    '''
    Ajoute les contraintes d'équilibre offre-demande avec de l'hydraulique
    (5.1.2)
    '''
    for t in range(24):
        model.addConstr(gp.quicksum([dict_P[X,t] for X in dict_Thermique])+gp.quicksum(dict_H[Y,t]*dict_Hydro[Y].P for Y in dict_Hydro)==consommation[t], name = f"Equilibre offre-demande à l'instant {t}")

def contraintes_reserve_avec_hydro(model,dict_N,dict_Thermique,dict_Hydro,consommation):
    '''
    Ajoute les contraintes de réserve de puissance avec de l'hydraulique
    (5.1.3)
    '''
    for t in range(24):
        model.addConstr(
            gp.quicksum([dict_N[X,t]*dict_Thermique[X].Pmax for X in dict_Thermique]) + 
            gp.quicksum([dict_Hydro[Y].P for Y in dict_Hydro])>= 1.15 * consommation[t], 
            name = f"Réserve de puissance à {t}")

# 5.2 ###############################################################################

def contraintes_reservoir(model,dict_S,dict_Hydro,dict_H,debit_S):
    '''
    Ajoute la contrainte d'équilibre du réservoir sur la journée
    '''
    model.addConstr(
        gp.quicksum([dict_S[t] * debit_S - gp.quicksum([dict_H[Y,t] * dict_Hydro[Y].debit for Y in dict_Hydro]) for t in range(24)])==0,
        name="Equilibre niveau réservoir"
    )

def contraintes_equilibre_avec_STEP(model,dict_H,dict_P,dict_Thermique,dict_Hydro,dict_S,consommation):
    '''
    Ajoute la contrainte d'équilibre offre-demande en prenant en compte le pompage
    '''
    for t in range(24):
        model.addConstr(
        gp.quicksum([dict_P[X,t] for X in dict_Thermique])+gp.quicksum(dict_H[Y,t]*dict_Hydro[Y].P for Y in dict_Hydro) - dict_S[t] ==consommation[t], 
        name = f"Equilibre offre-demande à l'instant {t}")

# 5.3 ###############################################################################

class Centrale_hydro2:
    '''
    Class permettant de regrouper les informations sur un type de centrale pour faciliter
    l'implementation du code
    '''
    def __init__(self, name, P, Cstart, Cheure, Palier, debit):
        self.name = name
        self.P = P
        self.Cstart = Cstart
        self.Cheure = Cheure
        self.Palier = Palier
        self.debit = debit
    def palier_max(self):
        return max(self.Palier)

def variables_decision_hydraulique_palier(model,dict_Hydro):
    '''
    Génère les variables de décision du problème liées à l'hydraulique
    output :
    dict_H[Y,n,t] dictionnaire contenant les VD sur le fonctionnement de la centrale Y au palier n à l'instant t
    dict_Hstart[Y,t] dictionnaire contenant les VD sur le démarrage des centrales Y à l'instant t
    '''
    dict_H = {}
    dict_Hstart = {}
    for Y in dict_Hydro:
        for t in range(24):
            dict_Hstart[Y,t] = model.addVar(vtype=gp.GRB.BINARY, name = f"Centrale Hydro {Y} démarre à l'heure {t}")
            for n in dict_Hydro[Y].Palier:
                dict_H[Y,n,t] = model.addVar(vtype=gp.GRB.BINARY, name = f"Centrale Hydro {Y} fonctionne au palier {n} à l'instant {t}")
    return dict_H, dict_Hstart

def contraintes_equilibre_palier(model,dict_P,dict_Thermique,dict_H,dict_Hydro,dict_S,consommation):
    '''
    Ajoute la contrainte d'équilibre offre-demande avec les paliers de l'hydraulique
    (5.3.1)
    '''
    for t in range(24):
        model.addConstr(
            gp.quicksum([dict_P[X,t] for X in dict_Thermique])+
            gp.quicksum([gp.quicksum([dict_H[Y,n,t]*dict_Hydro[Y].P[n] for n in dict_Hydro[Y].Palier]) for Y in dict_Hydro])
            -dict_S[t] == consommation[t],
            name = f"Equilibre offre-demande à l'instant {t}")

def contraintes_reserve_palier(model,dict_N,dict_Thermique,dict_Hydro,consommation):
    '''
    Ajoute la contrainte de réserve de puissance avec paliers hydraulique
    (5.3.2)
    '''
    for t in range(24):
        model.addConstr(
            gp.quicksum([dict_N[X,t]*dict_Thermique[X].Pmax for X in dict_Thermique]) + 
            gp.quicksum([dict_Hydro[Y].P[dict_Hydro[Y].palier_max()] for Y in dict_Hydro])>= 1.15 * consommation[t], 
            name = f"Réserve de puissance à {t}"
        )

def contraintes_reservoir_palier(model,dict_H,dict_Hydro,dict_S,debit_S):
    '''
    Ajoute la contrainte d'équilbre réservoir avec palier
    (5.3.3)
    '''
    model.addConstr(
    gp.quicksum([dict_S[t] * debit_S - gp.quicksum([gp.quicksum([dict_H[Y,n,t] * dict_Hydro[Y].debit[n] for n in dict_Hydro[Y].Palier]) for Y in dict_Hydro]) for t in range(24)])==0,
    name="Equilibre niveau réservoir"
    )

def contraintes_hydraulique_palier(model,dict_H,dict_Hydro,dict_Hstart):
    '''
    Ajoute les contraintes sur le fonctionnement des paliers hydraulique
    '''
    heures = np.arange(24)
    for t in range(24):
        for Y in dict_Hydro:
            # 5.3.4
            model.addConstr(
                gp.quicksum([dict_H[Y,n,t] for n in dict_Hydro[Y].Palier])<=1,
                name = f"Un seul palier en fonctionnement {t,Y}"
            )
            # 5.3.5
            model.addConstr(
                gp.quicksum([dict_H[Y,n,t] for n in dict_Hydro[Y].Palier]) <= gp.quicksum([dict_H[Y,n,heures[t-1]] for n in dict_Hydro[Y].Palier]) + dict_Hstart[Y,t]
            )

# 5.4 ###############################################################################

def contraintes_hydraulique_pompage(model,dict_H,dict_Hydro,dict_N_s,dict_S,M):
    '''
    Ajoute les contraintes sur l'exclusion de pompage en cas d'hydraulique
    '''
    for t in range(24):
        # 5.4.1
        model.addConstr(
            gp.quicksum([dict_H[Y,n,t] for Y in dict_Hydro for n in dict_Hydro[Y].Palier])/len(dict_Hydro) <= 1 - dict_N_s[t],
            name=f"Contrainte pompage selon fonctionnement hydro à {t}"
        )
        # 5.4.2
        model.addConstr(
            dict_S[t] <= M * dict_N_s[t],
            name=f"Contrainte fonctionnement pompage à {t}"
        )

#####################################################################################
# Partie 6
#####################################################################################

# 6.1 ###############################################################################
def variables_decision_desagregation_thermique(model,dict_Thermique):
    ''''
    Fontion générant les variables de décision
    Output :
    dict_N[X,k,t] dictionnaire contenant les VD sur la k-ieme centrale X en fonctionnement à l'instant t
    dict_P[X,k,t] dictionnaire contenant les VD de la puissance de la k-ieme centrales X à l'instant t
    dict_Nstart[X,k,t] dictionnaire contenant les VD sur la k-ieme centrale X démarre à l'instant t
    ''' 
    dict_N = {}
    dict_P = {}
    dict_Nstart = {}
    for t in range(24):
        for X in dict_Thermique:
            for k in range(dict_Thermique[X].N):
                dict_N[X,k,t] = model.addVar(vtype=gp.GRB.BINARY,name=f"centrale {X,k} fonctionne à {t}h")
                dict_P[X,k,t] = model.addVar(name=f"Puissance {X,k} à {t}h")
                dict_Nstart[X,k,t] = model.addVar(vtype=gp.GRB.BINARY,name=f"centrale {X,k} démarre à {t}h")
    return dict_N, dict_P, dict_Nstart

def contraintes_thermique_desagregation(model,dict_P,dict_N,dict_Nstart,dict_Thermique):
    '''
    Ajout des contraintes sur les centrales thermiques désagrégées
    '''
    heure = np.arange(24)
    for t in range(24):
        for X in dict_Thermique:
            for k in range(dict_Thermique[X].N):
                # (6.1.1)
                model.addConstr(
                    dict_P[X,k,t] <= dict_N[X,k,t] * dict_Thermique[X].Pmax, name=f"borne sup puissance {X,k,t}"
                )
                # (6.1.1)
                model.addConstr(
                    dict_P[X,k,t] >= dict_N[X,k,t] * dict_Thermique[X].Pmin, name=f"borne inf puissance {X,k,t}"
                )
                # (6.1.2)
                model.addConstr(
                    dict_N[X,k,t] <= dict_N[X,k,heure[t-1]] + dict_Nstart[X,k,t],name=f"Contrainte démarrage {X,k,t}"
                )

def contraintes_equilibre_desagregation(model,dict_P,dict_Thermique,dict_H,dict_Hydro,dict_S,consommation):
    '''
    Ajout des contraintes d'équilibre au modèle lorsque les centrales sont désagrégées
    (6.1.3)
    '''
    for t in range(24):
        model.addConstr(
            gp.quicksum([dict_P[X,k,t] for X in dict_Thermique for k in range(dict_Thermique[X].N)])+
            gp.quicksum([dict_H[Y,n,t] * dict_Hydro[Y].P[n] for Y in dict_Hydro for n in dict_Hydro[Y].Palier])-
            dict_S[t] == consommation[t], name=f"équilibre offre-demande à {t}"
        )

def contraintes_reserve_desagregation(model,dict_N,dict_Thermique,dict_Hydro,consommation):
    '''
    Ajout des contraintes de réserve au modèle lorsque les centrales sont désagrégées
    (6.1.4)
    '''
    for t in range(24):
        model.addConstr(
            gp.quicksum([dict_N[X,k,t]*dict_Thermique[X].Pmax for X in dict_Thermique for k in range(dict_Thermique[X].N)]) + 
            gp.quicksum([dict_Hydro[Y].P[dict_Hydro[Y].palier_max()] for Y in dict_Hydro])>= 1.15 * consommation[t], 
            name = f"Réserve de puissance à {t}"
        )

#####################################################################################
# Partie 7
#####################################################################################

# 7.1 ###############################################################################


#####################################################################################
# Partie 8
#####################################################################################

# 8.1 ###############################################################################

class Centrale3:
    '''
    Class permettant de regrouper les informations sur un type de centrale pour faciliter
    l'implementation du code
    '''
    def __init__(self, name, N, Pmin, Pmax, Cstart, Cbase, Cmwh, Rampe_Montante, Rampe_Start, Rampe_Descendante, Rampe_Stop):
        self.name = name
        self.N = N
        self.Pmin = Pmin
        self.Pmax = Pmax
        self.Cstart = Cstart
        self.Cbase = Cbase
        self.Cmwh = Cmwh
        self.Rampe_Montante = Rampe_Montante
        self.Rampe_Descendante = Rampe_Descendante
        self.Rampe_Start = Rampe_Start
        self.Rampe_Stop = Rampe_Stop

def contraintes_rampes(model,dict_P,dict_N,dict_Nstart,dict_Thermique):
    '''
    Ajoute les contraintes de rampes au modèle
    '''
    heure = np.arange(24)
    for t in range(24):
        for X in dict_Thermique:
            for k in range(dict_Thermique[X].N):
                    # 8.2
                model.addConstr(
                    dict_P[X,k,t]-dict_P[X,k,heure[t-1]]<=dict_Thermique[X].Rampe_Montante + (dict_N[X,k,t]-dict_N[X,k,heure[t-1]])*(dict_Thermique[X].Rampe_Start-dict_Thermique[X].Rampe_Montante),
                    name= f"Contraintes montantes {X,k}, à {t}"
                    )
                    #8.3
                model.addConstr(
                    dict_P[X,k,t]-dict_P[X,k,heure[t-1]]>=-dict_Thermique[X].Rampe_Descendante + (dict_N[X,k,t]-dict_N[X,k,heure[t-1]]-dict_Nstart[X,k,t])*(dict_Thermique[X].Rampe_Stop-dict_Thermique[X].Rampe_Descendante),
                    name= f"Contraintes descendantes {X,k}, à {t}"
                    )







