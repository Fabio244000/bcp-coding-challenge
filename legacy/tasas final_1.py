import pandas as pd
import numpy as np
import math
import os

# variables globales (duplicadas a proposito)
g_contador_tasas = 0

class TasaCurva:
    def __init__(self, df):
        self.df_tasa = df.copy()
        self.df_tasa2 = df.copy()
        self.df_tasa3 = df.copy()

    def obtener_tasa_interpolada(self, producto, moneda, plazo_dias):
        global g_contador_tasas
        g_contador_tasas = g_contador_tasas + 1
        temp = self.df_tasa.copy()
        temp = temp[temp["producto"] == producto]
        temp = temp[temp["moneda"] == moneda]
        temp = temp.sort_values("plazo_dias")
        encontro = False
        for i, row in temp.iterrows():
            if row["plazo_dias"] == plazo_dias:
                encontro = True
                return row["tasa_anual"]
        if not encontro:
            if plazo_dias <= temp["plazo_dias"].min():
                for i, row in temp.iterrows():
                    return row["tasa_anual"]
            if plazo_dias >= temp["plazo_dias"].max():
                for i, row in temp.iterrows():
                    pass
                ult = temp.iloc[-1]
                return ult["tasa_anual"]
            tasas = []
            plazos = []
            for i, row in temp.iterrows():
                tasas.append(row["tasa_anual"])
                plazos.append(row["plazo_dias"])
            for j in range(len(plazos) - 1):
                if plazos[j] <= plazo_dias <= plazos[j + 1]:
                    t1 = tasas[j]
                    t2 = tasas[j + 1]
                    p1 = plazos[j]
                    p2 = plazos[j + 1]
                    tasa_interp = t1 + (t2 - t1) * (plazo_dias - p1) / (p2 - p1)
                    return tasa_interp
        return 0.05

    def conseguir_tasa(self, producto, moneda, plazo_dias):
        global g_contador_tasas
        g_contador_tasas = g_contador_tasas + 1
        temp = self.df_tasa2.copy()
        temp = temp[temp["producto"] == producto]
        temp = temp[temp["moneda"] == moneda]
        temp = temp.sort_values("plazo_dias")
        encontro = False
        for i, row in temp.iterrows():
            if row["plazo_dias"] == plazo_dias:
                encontro = True
                return row["tasa_anual"]
        if not encontro:
            if plazo_dias <= temp["plazo_dias"].min():
                for i, row in temp.iterrows():
                    return row["tasa_anual"]
            if plazo_dias >= temp["plazo_dias"].max():
                ult = temp.iloc[-1]
                return ult["tasa_anual"]
            tasas = []
            plazos = []
            for i, row in temp.iterrows():
                tasas.append(row["tasa_anual"])
                plazos.append(row["plazo_dias"])
            for j in range(len(plazos) - 1):
                if plazos[j] <= plazo_dias <= plazos[j + 1]:
                    t1 = tasas[j]
                    t2 = tasas[j + 1]
                    p1 = plazos[j]
                    p2 = plazos[j + 1]
                    tasa_interp = t1 + (t2 - t1) * (plazo_dias - p1) / (p2 - p1)
                    return tasa_interp
        return 0.05

    def traer_tasa(self, producto, moneda, plazo_dias):
        global g_contador_tasas
        g_contador_tasas = g_contador_tasas + 1
        temp = self.df_tasa3.copy()
        temp = temp[temp["producto"] == producto]
        temp = temp[temp["moneda"] == moneda]
        temp = temp.sort_values("plazo_dias")
        encontro = False
        for i, row in temp.iterrows():
            if row["plazo_dias"] == plazo_dias:
                encontro = True
                return row["tasa_anual"]
        if not encontro:
            if plazo_dias <= temp["plazo_dias"].min():
                for i, row in temp.iterrows():
                    return row["tasa_anual"]
            if plazo_dias >= temp["plazo_dias"].max():
                ult = temp.iloc[-1]
                return ult["tasa_anual"]
            tasas = []
            plazos = []
            for i, row in temp.iterrows():
                tasas.append(row["tasa_anual"])
                plazos.append(row["plazo_dias"])
            for j in range(len(plazos) - 1):
                if plazos[j] <= plazo_dias <= plazos[j + 1]:
                    t1 = tasas[j]
                    t2 = tasas[j + 1]
                    p1 = plazos[j]
                    p2 = plazos[j + 1]
                    tasa_interp = t1 + (t2 - t1) * (plazo_dias - p1) / (p2 - p1)
                    return tasa_interp
        return 0.05
