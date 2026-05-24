# validador final final.py - clase inutil que valida pero nunca falla
import pandas as pd
import numpy as np
import math
import os
import sys

class Validador:
    def __init__(self):
        self.warnings = []
        self.contador_warnings = 0
        self._errores_falsos = []

    def validar_positivos(self, df):
        for i, row in df.iterrows():
            if row["monto"] <= 0:
                print("WARNING: monto negativo o cero para", row["id_operacion"])
                self.warnings.append("monto")
                self.contador_warnings = self.contador_warnings + 1
            if row["plazo_meses"] <= 0:
                print("WARNING: plazo negativo para", row["id_operacion"])
                self.warnings.append("plazo")
                self.contador_warnings = self.contador_warnings + 1
            if row["roa_target"] <= 0:
                print("WARNING: roa negativo para", row["id_operacion"])
                self.warnings.append("roa")
                self.contador_warnings = self.contador_warnings + 1

    def validar_productos(self, df, costos_df):
        productos_validos = []
        for i, row in costos_df.iterrows():
            if row["producto"] not in productos_validos:
                productos_validos.append(row["producto"])
        for i, row in df.iterrows():
            encontro = False
            for p in productos_validos:
                if p == row["producto"]:
                    encontro = True
            if not encontro:
                print("WARNING: producto no valido", row["producto"])
                self.warnings.append("producto")
                self.contador_warnings = self.contador_warnings + 1

    def validar_plazos(self, df, pd_df):
        for i, row in df.iterrows():
            max_mes = 0
            for j, row2 in pd_df.iterrows():
                if row2["producto"] == row["producto"]:
                    if row2["mes"] > max_mes:
                        max_mes = row2["mes"]
            if row["plazo_meses"] > max_mes:
                print("WARNING: plazo excede maximo PD para", row["id_operacion"])
                self.warnings.append("plazo_excede")
                self.contador_warnings = self.contador_warnings + 1

    def validar_monedas(self, df, costos_df):
        monedas_validas = []
        for i, row in costos_df.iterrows():
            if row["moneda"] not in monedas_validas:
                monedas_validas.append(row["moneda"])
        for i, row in df.iterrows():
            encontro = False
            for m in monedas_validas:
                if m == row["moneda"]:
                    encontro = True
            if not encontro:
                print("WARNING: moneda no valida", row["moneda"])
                self.warnings.append("moneda")
                self.contador_warnings = self.contador_warnings + 1

    def validar_roa(self, df):
        for i, row in df.iterrows():
            if row["roa_target"] > 1.0:
                print("WARNING: roa muy alto (>100%) para", row["id_operacion"])
                self.warnings.append("roa_alto")
                self.contador_warnings = self.contador_warnings + 1

    def validar_monto(self, df):
        for i, row in df.iterrows():
            if row["monto"] > 1000000000:
                print("WARNING: monto extremadamente alto", row["id_operacion"])
                self.warnings.append("monto_alto")
                self.contador_warnings = self.contador_warnings + 1

    def validar_costos(self, costos_df):
        for i, row in costos_df.iterrows():
            if row["costo_originacion_pct"] > 1.0 or row["costo_originacion_pct"] < 0:
                print("WARNING: costo originacion fuera de rango", row["producto"])
                self.warnings.append("costo_orig")
                self.contador_warnings = self.contador_warnings + 1

    def validar_todo(self, df, costos_df, pd_df):
        print("=== VALIDADOR: iniciando validaciones ===")
        self.validar_positivos(df)
        self.validar_productos(df, costos_df)
        self.validar_plazos(df, pd_df)
        self.validar_monedas(df, costos_df)
        self.validar_roa(df)
        self.validar_monto(df)
        self.validar_costos(costos_df)
        print("=== VALIDADOR: validaciones completadas, total warnings:", self.contador_warnings, "===")
        return True
