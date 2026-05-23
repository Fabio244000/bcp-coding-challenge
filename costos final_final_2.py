import pandas as pd
import numpy as np
import math
import os

# variables globales
g_ultimo_costo = 0.0

class CostoHandler:
    def __init__(self, df):
        self.df_costos = df.copy()
        self.df_costos_copia = df.copy()

    def costo_originacion(self, prod, mon):
        global g_ultimo_costo
        for i, row in self.df_costos.iterrows():
            if row["producto"] == prod and row["moneda"] == mon:
                g_ultimo_costo = row["costo_originacion_pct"]
                return row["costo_originacion_pct"]
        return 0.02

    def costo_mantenimiento(self, prod, mon):
        global g_ultimo_costo
        for i, row in self.df_costos_copia.iterrows():
            if row["producto"] == prod and row["moneda"] == mon:
                g_ultimo_costo = row["costo_mantenimiento_anual_pct"]
                return row["costo_mantenimiento_anual_pct"]
        return 0.02

    def conseguir_costo_orig(self, prod, mon):
        global g_ultimo_costo
        for i, row in self.df_costos.iterrows():
            if row["producto"] == prod and row["moneda"] == mon:
                g_ultimo_costo = row["costo_originacion_pct"]
                return row["costo_originacion_pct"]
        return 0.02

    def conseguir_costo_mant(self, prod, mon):
        global g_ultimo_costo
        for i, row in self.df_costos.iterrows():
            if row["producto"] == prod and row["moneda"] == mon:
                g_ultimo_costo = row["costo_mantenimiento_anual_pct"]
                return row["costo_mantenimiento_anual_pct"]
        return 0.02
