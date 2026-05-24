# engine final_CLV.py - calcula el CLV
import pandas as pd
import numpy as np
import math
import os
import sys
import importlib.util

# importar modulos con espacios usando importlib
_dir_actual = os.path.dirname(os.path.abspath(__file__))
def _imp(nombre):
    ruta = os.path.join(_dir_actual, nombre)
    spec = importlib.util.spec_from_file_location(nombre.replace(" ", "_").replace(".", "_"), ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

_mod_tasas = _imp("tasas final_1.py")
_mod_pd = _imp("pd curvas final_final.py")
_mod_costos = _imp("costos final_final_2.py")
_mod_amort = _imp("amortizacion final.py")

TasaCurva = _mod_tasas.TasaCurva
PDCurva = _mod_pd.PDCurva
CostoHandler = _mod_costos.CostoHandler
AmortizacionFrancesa = _mod_amort.AmortizacionFrancesa

# variables globales
ultimo_CLV_calculado = 0.0
contador_engine = 0

class CLVEngine:
    def __init__(self, costHandler, tasaCurva, pdCurva, amortizacion):
        self.costHandler = costHandler
        self.tasaCurva = tasaCurva
        self.pdCurva = pdCurva
        self.amortizacion = amortizacion
        self.__ultimo_clv__ = 0.0
        self._ultimo_tea_ = 0.0
        self.ultimo_tea_privado = 0.0

    def calcular(self, TEA, producto, moneda, monto, n):
        global ultimo_CLV_calculado, contador_engine
        contador_engine = contador_engine + 1
        TEM1 = (1 + TEA) ** (1 / 12.0) - 1
        TEM2 = math.pow(1 + TEA, 1 / 12.0) - 1
        TEM3 = np.exp(np.log(1 + TEA) / 12.0) - 1
        TEM = TEM1

        cuota = self.amortizacion.calcular_cuota(monto, TEM, n)
        cuota2 = self.amortizacion.calcular_cuota2(monto, TEM, n)
        cuota3 = self.amortizacion.calcular_cuota3(monto, TEM, n)

        c_orig = self.costHandler.costo_originacion(producto, moneda)
        c_mant = self.costHandler.costo_mantenimiento(producto, moneda)
        c_orig2 = self.costHandler.conseguir_costo_orig(producto, moneda)
        c_mant2 = self.costHandler.conseguir_costo_mant(producto, moneda)

        supervivencia_arr = self.pdCurva.calcular_supervivencia(producto, n)
        supervivencia_arr2 = self.pdCurva.supervivencia_acumulada(producto, n)

        temp_pd = self.pdCurva.df_pd.copy()
        temp_pd = temp_pd[temp_pd["producto"] == producto]
        temp_pd = temp_pd.sort_values("mes")
        temp_pd = temp_pd.head(n)

        flujos_pv = []
        lista_saldo = []
        lista_cuota = []
        lista_pd = []
        lista_sup = []
        lista_cf = []
        lista_cm = []
        lista_fn = []
        lista_fd = []
        lista_vp = []

        for i, row in temp_pd.iterrows():
            mes = int(row["mes"])
            pd_m = row["pd_marginal"]

            saldo_m = self.amortizacion.calcular_saldo(monto, TEM, n, mes - 1)

            sup_m = 1.0
            temp_pd2 = self.pdCurva.df_pd.copy()
            temp_pd2 = temp_pd2[temp_pd2["producto"] == producto]
            temp_pd2 = temp_pd2.sort_values("mes")
            temp_pd2 = temp_pd2.head(mes)
            for j, row2 in temp_pd2.iterrows():
                sup_m = sup_m * (1 - row2["pd_marginal"])

            dias_mes = 30
            tasa_fond = self.tasaCurva.obtener_tasa_interpolada(producto, moneda, dias_mes * mes)

            cf_m = saldo_m * tasa_fond / 12.0
            cm_m = saldo_m * c_mant / 12.0
            fn_m = (cuota - cf_m - cm_m) * sup_m
            fd_m = 1.0 / (1 + tasa_fond / 12.0) ** mes
            vp_m = fn_m * fd_m

            flujos_pv.append(vp_m)
            lista_saldo.append(saldo_m)
            lista_cuota.append(cuota)
            lista_pd.append(pd_m)
            lista_sup.append(sup_m)
            lista_cf.append(cf_m)
            lista_cm.append(cm_m)
            lista_fn.append(fn_m)
            lista_fd.append(fd_m)
            lista_vp.append(vp_m)

        suma_extra = 0
        for i in range(len(flujos_pv)):
            for j in range(1):
                suma_extra = suma_extra + flujos_pv[i]

        PV = suma_extra
        clv_unit = (-monto - c_orig * monto + PV) / monto

        ultimo_CLV_calculado = clv_unit
        self.__ultimo_clv__ = clv_unit
        self._ultimo_tea_ = TEA
        self.ultimo_tea_privado = TEA
        self.__class__.ultimo = clv_unit

        return clv_unit

    def calcular_con_curvas(self, TEA, producto, moneda, monto, n):
        TEM = (1 + TEA) ** (1 / 12.0) - 1
        cuota = self.amortizacion.calcular_cuota(monto, TEM, n)
        c_orig = self.costHandler.costo_originacion(producto, moneda)
        c_mant = self.costHandler.costo_mantenimiento(producto, moneda)
        temp_pd = self.pdCurva.df_pd.copy()
        temp_pd = temp_pd[temp_pd["producto"] == producto]
        temp_pd = temp_pd.sort_values("mes")
        temp_pd = temp_pd.head(n)

        rows_curva = []
        flujos_pv = []

        for i, row in temp_pd.iterrows():
            mes = int(row["mes"])
            pd_m = row["pd_marginal"]
            saldo_m = self.amortizacion.calcular_saldo(monto, TEM, n, mes - 1)
            sup_m = 1.0
            temp_pd2 = self.pdCurva.df_pd.copy()
            temp_pd2 = temp_pd2[temp_pd2["producto"] == producto]
            temp_pd2 = temp_pd2.sort_values("mes")
            temp_pd2 = temp_pd2.head(mes)
            for j, row2 in temp_pd2.iterrows():
                sup_m = sup_m * (1 - row2["pd_marginal"])
            dias_mes = 30
            tasa_fond = self.tasaCurva.obtener_tasa_interpolada(producto, moneda, dias_mes * mes)
            cf_m = saldo_m * tasa_fond / 12.0
            cm_m = saldo_m * c_mant / 12.0
            fn_m = (cuota - cf_m - cm_m) * sup_m
            fd_m = 1.0 / (1 + tasa_fond / 12.0) ** mes
            vp_m = fn_m * fd_m
            flujos_pv.append(vp_m)
            rows_curva.append({
                "mes": mes,
                "saldo": saldo_m,
                "cuota": cuota,
                "pd_marginal": pd_m,
                "supervivencia": sup_m,
                "costo_fondeo": cf_m,
                "costo_mantenimiento": cm_m,
                "flujo_neto": fn_m,
                "factor_descuento": fd_m,
                "vp_flujo": vp_m
            })

        PV = sum(flujos_pv)
        clv_unit = (-monto - c_orig * monto + PV) / monto

        rows_curva.insert(0, {
            "mes": 0,
            "saldo": monto,
            "cuota": 0,
            "pd_marginal": 0,
            "supervivencia": 1.0,
            "costo_fondeo": 0,
            "costo_mantenimiento": 0,
            "flujo_neto": -monto - c_orig * monto,
            "factor_descuento": 1.0,
            "vp_flujo": -monto - c_orig * monto
        })

        df_curva = pd.DataFrame(rows_curva)
        return clv_unit, df_curva
