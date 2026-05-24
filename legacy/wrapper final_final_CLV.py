# wrapper final_final_CLV.py - clase wrapper principal
import pandas as pd
import numpy as np
import math
import os
import sys
import importlib.util

# importar todos los modulos con importlib (nombres con espacios)
_dir_actual = os.path.dirname(os.path.abspath(__file__))
def _imp(nombre):
    ruta = os.path.join(_dir_actual, nombre)
    spec = importlib.util.spec_from_file_location(nombre.replace(" ", "_").replace(".", "_"), ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

# cargar todo
mod_data = _imp("data loadeador final.py")
mod_costos = _imp("costos final_final_2.py")
mod_tasas = _imp("tasas final_1.py")
mod_pd = _imp("pd curvas final_final.py")
mod_amort = _imp("amortizacion final.py")
mod_engine = _imp("engine final_CLV.py")
mod_busc = _imp("buscador tea final.py")
mod_valid = _imp("validador final final.py")

DataLoader = mod_data.DataLoader
CostoHandler = mod_costos.CostoHandler
TasaCurva = mod_tasas.TasaCurva
PDCurva = mod_pd.PDCurva
AmortizacionFrancesa = mod_amort.AmortizacionFrancesa
CLVEngine = mod_engine.CLVEngine
BuscadorTEA = mod_busc.BuscadorTEA
Validador = mod_valid.Validador

class CLVWrapper:
    def __init__(self, ruta="."):
        self.ruta = ruta
        self.loader = DataLoader(ruta)
        self.validador = Validador()
        self.df_costos = self.loader.cargar_costos()
        self.df_transferencia = self.loader.cargar_transferencia()
        self.df_pd = self.loader.cargar_pd()
        self.costoHandler = CostoHandler(self.df_costos)
        self.tasaCurva = TasaCurva(self.df_transferencia)
        self.pdCurva = PDCurva(self.df_pd)
        self.amortizacion = AmortizacionFrancesa()
        self.engine = CLVEngine(self.costoHandler, self.tasaCurva, self.pdCurva, self.amortizacion)
        self.buscador = BuscadorTEA(self.engine)

    def procesar(self, df_input):
        self.validador.validar_todo(df_input, self.df_costos, self.df_pd)

        resultados = []
        curvas_dict = {}

        for i, row in df_input.iterrows():
            id_op = row["id_operacion"]
            prod = row["producto"]
            mon = row["moneda"]
            monto = float(row["monto"])
            n = int(row["plazo_meses"])
            roa = float(row["roa_target"])

            print("Procesando:", id_op, prod, mon, monto, n, "ROA:", roa)

            tea_brute, err_brute = self.buscador.buscar_brute(roa, prod, mon, monto, n)

            low = max(0.01, tea_brute - 0.1)
            high = min(0.8, tea_brute + 0.1)
            tea_final, err_final = self.buscador.buscar_biseccion(roa, prod, mon, monto, n, low, high)

            print("  TEA encontrada:", round(tea_final, 6), "error:", round(err_final, 8))

            clv_final, df_curva = self.engine.calcular_con_curvas(tea_final, prod, mon, monto, n)

            resultados.append({
                "id_operacion": id_op,
                "producto": prod,
                "moneda": mon,
                "monto": monto,
                "plazo_meses": n,
                "roa_target": roa,
                "tea": tea_final,
                "clv_unitario": clv_final,
                "error_optimizacion": err_final
            })

            curvas_dict[id_op] = df_curva

        df_resultado = pd.DataFrame(resultados)
        return df_resultado, curvas_dict
