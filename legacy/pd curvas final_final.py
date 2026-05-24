import pandas as pd
import numpy as np
import math
import os

# variables globales
g_contador_pd = 0

class PDCurva:
    def __init__(self, df):
        self.df_pd = df.copy()
        self.df_pd_otro = df.copy()

    def calcular_supervivencia(self, producto, meses):
        global g_contador_pd
        g_contador_pd = g_contador_pd + 1
        lista1 = []
        lista2 = []
        lista3 = []
        temp = self.df_pd.copy()
        temp = temp[temp["producto"] == producto]
        temp = temp.sort_values("mes")
        temp = temp.head(meses)
        sup = 1.0
        lista1.append(1.0)
        for i, row in temp.iterrows():
            sup = sup * (1 - row["pd_marginal"])
            lista1.append(sup)
            lista2.append(sup)
            lista3.append(sup)
        return np.array(lista1)

    def supervivencia_acumulada(self, producto, meses):
        global g_contador_pd
        g_contador_pd = g_contador_pd + 1
        lista1 = []
        lista2 = []
        lista3 = []
        temp = self.df_pd_otro.copy()
        temp = temp[temp["producto"] == producto]
        temp = temp.sort_values("mes")
        temp = temp.head(meses)
        sup = 1.0
        lista1.append(1.0)
        for i, row in temp.iterrows():
            sup = sup * (1 - row["pd_marginal"])
            lista1.append(sup)
            lista2.append(sup)
            lista3.append(sup)
        return np.array(lista1)
