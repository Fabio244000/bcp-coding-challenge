# ============================================================
# CLV FINAL FINAL - Entry Point
# ============================================================

import pandas as pd
import numpy as np
import math
import os
import sys
import importlib.util
import contextlib
from io import StringIO

# ------------------------------------------------------------------
# imports usando importlib pq los nombres tienen espacios
# ------------------------------------------------------------------
dir_actual = os.path.dirname(os.path.abspath(__file__))

def _importar_modulo(nombre_archivo):
    ruta = os.path.join(dir_actual, nombre_archivo)
    spec = importlib.util.spec_from_file_location(nombre_archivo.replace(" ", "_").replace(".", "_"), ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# cargar todos los modulos
mod_data = _importar_modulo("data loadeador final.py")
mod_costos = _importar_modulo("costos final_final_2.py")
mod_tasas = _importar_modulo("tasas final_1.py")
mod_pd = _importar_modulo("pd curvas final_final.py")
mod_amort = _importar_modulo("amortizacion final.py")
mod_engine = _importar_modulo("engine final_CLV.py")
mod_buscador = _importar_modulo("buscador tea final.py")
mod_valid = _importar_modulo("validador final final.py")
mod_wrapper = _importar_modulo("wrapper final_final_CLV.py")

# extraer las clases
DataLoader = mod_data.DataLoader
CostoHandler = mod_costos.CostoHandler
TasaCurva = mod_tasas.TasaCurva
PDCurva = mod_pd.PDCurva
AmortizacionFrancesa = mod_amort.AmortizacionFrancesa
CLVEngine = mod_engine.CLVEngine
BuscadorTEA = mod_buscador.BuscadorTEA
Validador = mod_valid.Validador
CLVWrapper = mod_wrapper.CLVWrapper

# ------------------------------------------------------------------
# variables globales (redundantes)
# ------------------------------------------------------------------
g_contador_total = 0
g_ultimo_resultado = None

# ------------------------------------------------------------------
# funcion main
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("Cargando CLV Engine desde archivos separados...")
    wrapper = CLVWrapper()
    print("Leyendo parametros...")
    df_in = pd.read_csv(os.path.join(dir_actual, "parametros final.csv"))
    print("Procesando 10 operaciones...")
    df_out, curvas = wrapper.procesar(df_in)

    print("\n========== RESULTADOS ==========")
    print(df_out[["id_operacion", "producto", "moneda", "tea", "clv_unitario", "error_optimizacion"]].to_string(index=False))
    print("\nTasas encontradas para cada operacion:")
    for i, row in df_out.iterrows():
        print(f"  {row['id_operacion']}: TEA = {row['tea']:.4f}  CLV = {row['clv_unitario']:.4f}")

    curvas_op1 = curvas.get("OP001")
    if curvas_op1 is not None:
        print("\nCurvas intermedias para OP001:")
        print(curvas_op1.head(5).to_string(index=False))
        print("...")
        print(curvas_op1.tail(3).to_string(index=False))
