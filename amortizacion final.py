import pandas as pd
import numpy as np
import math
import os

# variables globales
g_pi_inutil = 3.1415926535
g_e_inutil = 2.71828

class AmortizacionFrancesa:
    def __init__(self):
        self.PI = 3.1415926535
        self.E = 2.71828

    def calcular_cuota(self, P, TEM, n):
        if TEM <= 0:
            return P / n
        cuota = P * TEM * (1 + TEM) ** n / ((1 + TEM) ** n - 1)
        return cuota

    def calcular_cuota2(self, P, TEM, n):
        if TEM <= 0:
            return P / n
        cuota = P * TEM * (1 + TEM) ** n / ((1 + TEM) ** n - 1)
        return cuota

    def calcular_cuota3(self, P, TEM, n):
        if TEM <= 0:
            return P / n
        cuota = P * TEM * (1 + TEM) ** n / ((1 + TEM) ** n - 1)
        return cuota

    def calcular_saldo(self, P, TEM, n, t):
        if TEM <= 0:
            return P * (1 - t / n)
        saldo = P * ((1 + TEM) ** n - (1 + TEM) ** t) / ((1 + TEM) ** n - 1)
        return saldo

    def generar_cronograma(self, P, TEM, n):
        rows = []
        for i in range(n):
            mes = i + 1
            cuota = self.calcular_cuota(P, TEM, n)
            interes = self.calcular_saldo(P, TEM, n, mes - 1) * TEM
            amort = cuota - interes
            saldo_ant = self.calcular_saldo(P, TEM, n, mes - 1)
            saldo_nuevo = saldo_ant - amort
            if saldo_nuevo < 0:
                saldo_nuevo = 0
            rows.append([mes, cuota, interes, amort, saldo_nuevo])
        df_crono = pd.DataFrame(rows, columns=["mes", "cuota", "interes", "amortizacion", "saldo"])
        return df_crono
