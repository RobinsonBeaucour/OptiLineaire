import gurobipy as gp
from itertools import product
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils  import division
from turtle import color
import plotly.graph_objects as go

def df_results(dict_N,dict_P,dict_XX,consommation):
    df = pd.DataFrame()
    df["h"] = range(24) 
    df["Consommation (MW)"] = consommation
    df["Production total"] = 0
    df["Coût total"] = 0
    for X in dict_XX:
        df[f"Nb centrale {X}"] = [int(dict_N[X,t].X) for t in range(24)]
        df[f"Puissance tot {X}"] = [dict_P[X,t].X for t in range(24)]
        df[f"Coût {X}"] = [dict_P[X,t].X * dict_XX[X].Cmwh for t in range(24)]
        df[f"Facteur de charge{X}"] = [int(division(dict_P[X,t].X ,dict_N[X,t].X * dict_XX[X].Pmax)*100) for t in range(24)]
        df["Production total"] += df[f"Puissance tot {X}"]
        df["Coût total"] += df[f"Coût {X}"]
    df["Coût MWh"] = df["Coût total"]/df["Production total"]
    return df

def Results_viz(df,dict_Thermique):
    fig = go.Figure()

    for X in dict_Thermique:
        fig.add_trace(
            go.Scatter(
            x=df["h"], 
            y=df[f"Puissance tot {X}"], 
            name = f"Production {X}",
            stackgroup="one"
            )
        )

    # fig.add_trace(
    #     go.Scatter(
    #         x = df["h"],
    #         y = df["Consommation (MW)"],
    #         name = "Consommation"
    #     )
    # )
    fig.add_trace(
        go.Scatter(
            x = df["h"],
            y = df["Production total"],
            name="Production total",
            line = dict(dash='dash',color="red")
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["h"],
            y=df["Coût MWh"],
            yaxis="y2",
            name="Coût MWh",
            line_color="black"
        )
    )

    fig.update_layout(
        hovermode='x',
        yaxis=dict(title="MW" ,range=[0,df["Consommation (MW)"].max()*1.1]),
        yaxis2=dict(title="€/MWh",
        range=[df["Coût MWh"].min()*0.95,df["Coût MWh"].max()*1.1],
        anchor="free",
        overlaying="y",
        side="right",
        position=1
        ),
        title = "Répartition de la production électrique dans la journée"
    )
    return fig

def df_results2(dict_N,dict_P,dict_XX,consommation):
    df = pd.DataFrame()
    df["h"] = range(24) 
    df["Consommation (MW)"] = consommation
    df["Production total"] = 0
    df["Coût total"] = 0
    for X in dict_XX:
        df[f"Nb centrale {X}"] = [int(dict_N[X,t].X) for t in range(24)]
        df[f"Puissance tot {X}"] = [dict_P[X,t].X for t in range(24)]
        df[f"Coût {X}"] = [dict_N[X,t].X * dict_XX[X].Cbase + (dict_P[X,t].X - dict_N[X,t].X * dict_XX[X].Pmin) * dict_XX[X].Cmwh for t in range(24)]
        df["Production total"] += df[f"Puissance tot {X}"]
        df["Coût total"] += df[f"Coût {X}"]
    df["Coût MWh"] = df["Coût total"]/df["Production total"]
    return df

def df_results22(dict_N,dict_P,dict_Nstart,dict_XX,consommation):
    df = pd.DataFrame()
    df["h"] = range(24) 
    df["Consommation (MW)"] = consommation
    df["Production total"] = 0
    df["Coût total"] = 0
    for X in dict_XX:
        df[f"Nb centrale {X}"] = [int(dict_N[X,t].X) for t in range(24)]
        df[f"Puissance tot {X}"] = [dict_P[X,t].X for t in range(24)]
        df[f"Coût {X}"] = [dict_N[X,t].X * dict_XX[X].Cbase + (dict_P[X,t].X - dict_N[X,t].X * dict_XX[X].Pmin) * dict_XX[X].Cmwh + dict_Nstart[X,t].X*dict_XX[X].Cstart for t in range(24)]
        df["Production total"] += df[f"Puissance tot {X}"]
        df["Coût total"] += df[f"Coût {X}"]
    df["Coût MWh"] = df["Coût total"]/df["Production total"]
    return df

def df_results5(dict_N,dict_P,dict_Nstart,dict_Thermique,dict_H,dict_Hstart,dict_Hydro,consommation):
    df = df_results22(dict_N,dict_P,dict_Nstart,dict_Thermique,consommation)
    for Y in dict_Hydro:
        df[f"Fonctionnement {Y}"] = [dict_H[Y,t].X for t in range(24)]
        df[f"Puissance tot {Y}"] = [dict_H[Y,t].X * dict_Hydro[Y].P for t in range(24)]
        df[f"Coût {Y}"] = [dict_H[Y,t].X * dict_Hydro[Y].Cheure + dict_Hstart[Y,t].X * dict_Hydro[Y].Cstart for t in range(24)]
        df["Production total"] += df[f"Puissance tot {Y}"]
        df["Coût total"] += df[f"Coût {Y}"]
    df["Coût MWh"] = df["Coût total"]/df["Production total"]
    return df

def Results_viz5(df,dict_Thermique,dict_Hydro):
    fig = go.Figure()

    for X in dict_Thermique:
        fig.add_trace(
            go.Scatter(
            x=df["h"], 
            y=df[f"Puissance tot {X}"], 
            stackgroup="one",
            name = f"Thermique {X}"
            )
        )
    for Y in dict_Hydro:
        fig.add_trace(
            go.Scatter(
            x=df["h"], 
            y=df[f"Puissance tot {Y}"], 
            stackgroup="one",
            name = f"Hydraulique {Y}"
            )
        )

    fig.add_trace(
        go.Scatter(
            x = df["h"],
            y = df["Production total"],
            name="Production total",
            line = dict(dash='dash',color="red")
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["h"],
            y=df["Coût MWh"],
            yaxis="y2",
            name="Coût MWh",
            line_color="black"
        )
    )

    fig.update_layout(
        hovermode='x',
        yaxis=dict(title="MW" ,range=[0,df["Consommation (MW)"].max()*1.1]),
        yaxis2=dict(title="€/MWh",
        range=[df["Coût MWh"].min()*0.95,df["Coût MWh"].max()*1.1],
        anchor="free",
        overlaying="y",
        side="right",
        position=1
        ),
        title = "Répartition de la production électrique dans la journée"
    )
    return fig

def df_results52(dict_N,dict_P,dict_Nstart,dict_Thermique,dict_H,dict_Hstart,dict_Hydro,dict_S,debit_S,consommation):
    df = pd.DataFrame()
    df["h"] = range(24) 
    df["Consommation (MW)"] = consommation
    df["Production total"] = 0
    df["Coût total"] = 0
    for X in dict_Thermique:
        df[f"Nb centrale {X}"] = [int(dict_N[X,t].X) for t in range(24)]
        df[f"Puissance tot {X}"] = [dict_P[X,t].X for t in range(24)]
        df[f"Coût {X}"] = [dict_N[X,t].X * dict_Thermique[X].Cbase + (dict_P[X,t].X - dict_N[X,t].X * dict_Thermique[X].Pmin) * dict_Thermique[X].Cmwh + dict_Nstart[X,t].X*dict_Thermique[X].Cstart for t in range(24)]
        df["Production total"] += df[f"Puissance tot {X}"]
        df["Coût total"] += df[f"Coût {X}"]
    for Y in dict_Hydro:
        df[f"Fonctionnement {Y}"] = [dict_H[Y,t].X for t in range(24)]
        df[f"Démarrage {Y}"] = [dict_Hstart[Y,t].X for t in range(24)]
        df[f"Puissance tot {Y}"] = [dict_H[Y,t].X * dict_Hydro[Y].P for t in range(24)]
        df[f"Coût {Y}"] = [dict_H[Y,t].X * dict_Hydro[Y].Cheure + dict_Hstart[Y,t].X * dict_Hydro[Y].Cstart for t in range(24)]
        df["Production total"] += df[f"Puissance tot {Y}"]
        df["Coût total"] += df[f"Coût {Y}"]
    df["Pompage"] = [-dict_S[t].X for t in range(24)]
    df["Production total"] += df["Pompage"]
    df["Réservoir variation"] = [dict_S[t].X * debit_S - sum([dict_H[Y,t].X * dict_Hydro[Y].debit for Y in dict_Hydro]) for t in range(24)]
    df["Réservoir"] = df["Réservoir variation"].cumsum()
    df["Coût MWh"] = df["Coût total"]/df["Production total"]
    return df

def Results_viz52(df,dict_Thermique,dict_Hydro):
    fig = go.Figure()

    for X in dict_Thermique:
        fig.add_trace(
            go.Scatter(
            x=df["h"], 
            y=df[f"Puissance tot {X}"], 
            stackgroup="one",
            name = f"Thermique {X}"
            )
        )
    for Y in dict_Hydro:
        fig.add_trace(
            go.Scatter(
            x=df["h"], 
            y=df[f"Puissance tot {Y}"], 
            stackgroup="one",
            name = f"Hydraulique {Y}"
            )
        )
    fig.add_trace(
        go.Scatter(
        x=df["h"], 
        y=df["Pompage"], 
        stackgroup="two",
        name = "Pompage"
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x = df["h"],
            y = df["Production total"],
            name="Production total",
            line = dict(dash='dash',color="red")
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["h"],
            y=df["Coût MWh"],
            yaxis="y2",
            name="Coût MWh",
            line_color="black"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["h"],
            y=df["Réservoir"],
            yaxis="y3",
            name="Niveau réservoir",
            line_color="grey"
        )
    )

    fig.update_layout(
        hovermode='x',
        yaxis=dict(title="MW" ,range=[df["Pompage"].min()*1.1,df["Consommation (MW)"].max()*1.1]),
        yaxis2=dict(
            title="€/MWh",
            range=[df["Coût MWh"].min()*0.95,df["Coût MWh"].max()*1.1],
            anchor="free",
            overlaying="y",
            side="right",
            position=1
            ),
        yaxis3=dict(
            title="Réservoir (m)",
            range=[df["Réservoir"].min()*1.1,df["Réservoir"].max()*1.1],
            anchor="free",
            overlaying="y",
            side="left",
            position=0.05
            ),
        title = "Répartition de la production électrique dans la journée"
    )
    return fig

def df_results53(dict_N,dict_P,dict_Nstart,dict_Thermique,dict_H,dict_Hstart,dict_Hydro,dict_S,debit_S,consommation):
    df = pd.DataFrame()
    df["h"] = range(24) 
    df["Consommation (MW)"] = consommation
    df["Production total"] = 0
    df["Coût total"] = 0
    for X in dict_Thermique:
        df[f"Nb centrale {X}"] = [int(dict_N[X,t].X) for t in range(24)]
        df[f"Puissance tot {X}"] = [dict_P[X,t].X for t in range(24)]
        df[f"Coût {X}"] = [dict_N[X,t].X * dict_Thermique[X].Cbase + (dict_P[X,t].X - dict_N[X,t].X * dict_Thermique[X].Pmin) * dict_Thermique[X].Cmwh + dict_Nstart[X,t].X*dict_Thermique[X].Cstart for t in range(24)]
        df["Production total"] += df[f"Puissance tot {X}"]
        df["Coût total"] += df[f"Coût {X}"]
    for Y in dict_Hydro:
        for n in dict_Hydro[Y].Palier:
            df[f"Fonctionnement {Y}, palier {n}"] = [dict_H[Y,n,t].X for t in range(24)]
            df[f"Puissance tot {Y}, palier {n}"] = [dict_H[Y,n,t].X * dict_Hydro[Y].P[n] for t in range(24)]
            df[f"Coût {Y}, palier {n}"] = [dict_H[Y,n,t].X * dict_Hydro[Y].Cheure[n] for t in range(24)]
        df[f"Démarrage {Y}"] = [dict_Hstart[Y,t].X for t in range(24)]
        df[f"Fonctionnement {Y}"] = [sum(dict_H[Y,n,t].X for n in dict_Hydro[Y].Palier) for t in range(24)]
        df[f"Puissance tot {Y}"] = df[[f"Puissance tot {Y}, palier {n}" for n in dict_Hydro[Y].Palier]].sum(1)
        df[f"Coût {Y}"] = df[[f"Coût {Y}, palier {n}" for n in dict_Hydro[Y].Palier]].sum(1) + pd.DataFrame([dict_Hstart[Y,t].X * dict_Hydro[Y].Cstart for t in range(24)])[0]
        df["Production total"] += df[f"Puissance tot {Y}"]
        df["Coût total"] += df[f"Coût {Y}"]
    df["Pompage"] = [-dict_S[t].X for t in range(24)]
    df["Production total"] += df["Pompage"]
    df["Réservoir variation"] = [dict_S[t].X * debit_S - sum([dict_H[Y,n,t].X * dict_Hydro[Y].debit[n] for Y in dict_Hydro for n in dict_Hydro[Y].Palier]) for t in range(24)]
    df["Réservoir"] = df["Réservoir variation"].cumsum()
    df["Coût MWh"] = df["Coût total"]/df["Production total"]
    return df

def df_results61(dict_N,dict_P,dict_Nstart,dict_Thermique,dict_H,dict_Hstart,dict_Hydro,dict_S,debit_S,consommation):
    df = pd.DataFrame()
    df["h"] = range(24) 
    df["Consommation (MW)"] = consommation
    df["Production total"] = 0
    df["Coût total"] = 0
    for X in dict_Thermique:
        for k in range(dict_Thermique[X].N):
            df[f"centrale {X,k}"] = [int(dict_N[X,k,t].X) for t in range(24)]
            df[f"Puissance {X,k}"] = [dict_P[X,k,t].X for t in range(24)]
            df[f"Coût {X,k}"] = [dict_N[X,k,t].X * dict_Thermique[X].Cbase + (dict_P[X,k,t].X - dict_N[X,k,t].X * dict_Thermique[X].Pmin) * dict_Thermique[X].Cmwh + dict_Nstart[X,k,t].X*dict_Thermique[X].Cstart for t in range(24)]
            df["Production total"] += df[f"Puissance {X,k}"]
            df["Coût total"] += df[f"Coût {X,k}"]
        df[f"Puissance tot {X}"] = df[[f"Puissance {X,k}" for k in range(dict_Thermique[X].N)]].sum(1)
    for Y in dict_Hydro:
        for n in dict_Hydro[Y].Palier:
            df[f"Fonctionnement {Y}, palier {n}"] = [dict_H[Y,n,t].X for t in range(24)]
            df[f"Puissance tot {Y}, palier {n}"] = [dict_H[Y,n,t].X * dict_Hydro[Y].P[n] for t in range(24)]
            df[f"Coût {Y}, palier {n}"] = [dict_H[Y,n,t].X * dict_Hydro[Y].Cheure[n] for t in range(24)]
        df[f"Démarrage {Y}"] = [dict_Hstart[Y,t].X for t in range(24)]
        df[f"Fonctionnement {Y}"] = [sum(dict_H[Y,n,t].X for n in dict_Hydro[Y].Palier) for t in range(24)]
        df[f"Puissance tot {Y}"] = df[[f"Puissance tot {Y}, palier {n}" for n in dict_Hydro[Y].Palier]].sum(1)
        df[f"Coût {Y}"] = df[[f"Coût {Y}, palier {n}" for n in dict_Hydro[Y].Palier]].sum(1) + pd.DataFrame([dict_Hstart[Y,t].X * dict_Hydro[Y].Cstart for t in range(24)])[0]
        df["Production total"] += df[f"Puissance tot {Y}"]
        df["Coût total"] += df[f"Coût {Y}"]
    df["Pompage"] = [-dict_S[t].X for t in range(24)]
    df["Production total"] += df["Pompage"]
    df["Réservoir variation"] = [dict_S[t].X * debit_S - sum([dict_H[Y,n,t].X * dict_Hydro[Y].debit[n] for Y in dict_Hydro for n in dict_Hydro[Y].Palier]) for t in range(24)]
    df["Réservoir"] = df["Réservoir variation"].cumsum()
    df["Coût MWh"] = df["Coût total"]/df["Production total"]
    return df


    
    






