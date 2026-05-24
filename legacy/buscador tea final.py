# buscador tea final.py - optimizacion ineficiente
import pandas as pd
import numpy as np
import math
import os
import sys
import importlib.util

# importar engine con importlib
_dir_actual = os.path.dirname(os.path.abspath(__file__))
spec_eng = importlib.util.spec_from_file_location("engine_final", os.path.join(_dir_actual, "engine final_CLV.py"))
mod_eng = importlib.util.module_from_spec(spec_eng)
spec_eng.loader.exec_module(mod_eng)
CLVEngine = mod_eng.CLVEngine

# variables globales
lista_tea_busqueda = []
lista_error_busqueda = []

class BuscadorTEA:
    def __init__(self, engine):
        self.engine = engine
        self.__lista_errores = []
        self._lista_tasas_ = []

    def buscar_brute(self, roa_target, producto, moneda, monto, n):
        global lista_tea_busqueda, lista_error_busqueda
        mejor_tea = 0.05
        mejor_error = 99999.0
        tea = 0.01
        while tea <= 0.8:
            clv = self.engine.calcular(tea, producto, moneda, monto, n)
            error = abs(clv - roa_target)
            if error < mejor_error:
                mejor_error = error
                mejor_tea = tea
            lista_tea_busqueda.append(tea)
            lista_error_busqueda.append(error)
            self.__lista_errores.append(error)
            self._lista_tasas_.append(tea)
            tea = tea + 0.05
        return mejor_tea, mejor_error

    def buscar_biseccion(self, roa_target, producto, moneda, monto, n, low, high):
        global lista_tea_busqueda, lista_error_busqueda
        mejor_tea = low
        mejor_error = 99999.0
        lo = low
        hi = high
        for iteracion in range(30):
            mid = (lo + hi) / 2.0
            clv_mid = self.engine.calcular(mid, producto, moneda, monto, n)
            clv_lo = self.engine.calcular(lo, producto, moneda, monto, n)
            error_mid = abs(clv_mid - roa_target)
            lista_tea_busqueda.append(mid)
            lista_error_busqueda.append(error_mid)
            if error_mid < mejor_error:
                mejor_error = error_mid
                mejor_tea = mid
            if clv_mid * clv_lo > 0:
                lo = mid
            else:
                hi = mid
        return mejor_tea, mejor_error
