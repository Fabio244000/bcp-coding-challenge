import unittest
import pandas as pd
import numpy as np
import os
import sys
import contextlib
from io import StringIO
import importlib.util

# importar usando importlib por los espacios en nombres
dir_actual = os.path.dirname(os.path.abspath(__file__))
ruta_wrapper = os.path.join(dir_actual, "wrapper final_final_CLV.py")
ruta_validador = os.path.join(dir_actual, "validador final final.py")

spec_w = importlib.util.spec_from_file_location("wrapper_final_final", ruta_wrapper)
mod_w = importlib.util.module_from_spec(spec_w)
spec_w.loader.exec_module(mod_w)

spec_v = importlib.util.spec_from_file_location("validador_final", ruta_validador)
mod_v = importlib.util.module_from_spec(spec_v)
spec_v.loader.exec_module(mod_v)

CLVWrapper = mod_w.CLVWrapper
Validador = mod_v.Validador

print("=" * 60)
print("TEST CLV - 10 OPERACIONES")
print("=" * 60)


class TestCLVcon10Operaciones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir_actual = os.path.dirname(os.path.abspath(__file__))
        cls.ruta = cls.dir_actual
        cls.df_params = pd.read_csv(os.path.join(cls.dir_actual, "parametros final.csv"))
        cls.df_costos = pd.read_csv(os.path.join(cls.dir_actual, "costos final_1.csv"))
        cls.df_trans = pd.read_csv(os.path.join(cls.dir_actual, "transferencia final_final.csv"))
        cls.df_pd = pd.read_csv(os.path.join(cls.dir_actual, "pd final_final_2.csv"))
        with contextlib.redirect_stdout(StringIO()):
            cls.wrapper = CLVWrapper(cls.ruta)

    def setUp(self):
        self.df_10ops = pd.read_csv(os.path.join(self.dir_actual, "parametros final.csv"))

    def test_resultado_tiene_columnas(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, _ = self.wrapper.procesar(self.df_10ops)
        self.assertIn("id_operacion", df_res.columns)
        self.assertIn("tea", df_res.columns)

    def test_resultado_tiene_10_filas(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, _ = self.wrapper.procesar(self.df_10ops)
        self.assertEqual(len(df_res), 10)

    def test_tea_no_nula(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, _ = self.wrapper.procesar(self.df_10ops)
        self.assertFalse(df_res["tea"].isna().any())

    def test_tea_rango_razonable(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, _ = self.wrapper.procesar(self.df_10ops)
        for i, row in df_res.iterrows():
            print(row["tea"])
            self.assertGreaterEqual(row["tea"], 0.01, f"TEA muy baja para {row['id_operacion']}")
            self.assertLessEqual(row["tea"], 0.99, f"TEA muy alta para {row['id_operacion']}")

    def test_curvas_existen_para_cada_id(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, curvas = self.wrapper.procesar(self.df_10ops)
        for i, row in df_res.iterrows():
            id_op = row["id_operacion"]
            self.assertIn(id_op, curvas, f"Faltan curvas para {id_op}")

    def test_curvas_tiene_columnas_esperadas(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, curvas = self.wrapper.procesar(self.df_10ops)
        columnas_esperadas = ["mes", "saldo", "cuota", "pd_marginal", "supervivencia",
                              "costo_fondeo", "costo_mantenimiento", "flujo_neto",
                              "factor_descuento", "vp_flujo"]
        for id_op, df_curva in curvas.items():
            for col in columnas_esperadas:
                self.assertIn(col, df_curva.columns, f"Falta columna {col} en curvas de {id_op}")

    def test_curvas_tiene_n_meses_mas_cero(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, curvas = self.wrapper.procesar(self.df_10ops)
        for i, row in df_res.iterrows():
            id_op = row["id_operacion"]
            n_esperado = int(row["plazo_meses"]) + 1
            n_actual = len(curvas[id_op])
            self.assertEqual(n_actual, n_esperado,
                f"Curvas de {id_op}: esperado {n_esperado}, obtenido {n_actual}")

    def test_ids_unicos(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, _ = self.wrapper.procesar(self.df_10ops)
        ids = df_res["id_operacion"].tolist()
        self.assertEqual(len(ids), len(set(ids)), "Hay IDs duplicados")

    def test_tea_mayor_que_tasa_fondeo_base(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, _ = self.wrapper.procesar(self.df_10ops)
        for i, row in df_res.iterrows():
            tasa_fondeo_base = self.df_trans[
                (self.df_trans["producto"] == row["producto"]) &
                (self.df_trans["moneda"] == row["moneda"])
            ]["tasa_anual"].min()
            self.assertGreaterEqual(row["tea"], tasa_fondeo_base,
                f"TEA {row['tea']} < tasa fondeo {tasa_fondeo_base} para {row['id_operacion']}")

    def test_setup_carga_csv(self):
        self.assertIsNotNone(self.df_params)
        self.assertIsNotNone(self.df_costos)
        self.assertIsNotNone(self.df_trans)
        self.assertIsNotNone(self.df_pd)
        self.assertEqual(len(self.df_params), 10)
        self.assertEqual(len(self.df_costos), 6)

    def test_curvas_mes0_saldo_igual_monto(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, curvas = self.wrapper.procesar(self.df_10ops)
        for i, row in df_res.iterrows():
            id_op = row["id_operacion"]
            df_c = curvas[id_op]
            fila0 = df_c[df_c["mes"] == 0]
            self.assertAlmostEqual(fila0["saldo"].values[0], row["monto"], delta=0.01,
                msg=f"Saldo mes 0 incorrecto para {id_op}")

    def test_supervivencia_entre_0_y_1(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, curvas = self.wrapper.procesar(self.df_10ops)
        for id_op, df_c in curvas.items():
            for i, row in df_c.iterrows():
                self.assertGreaterEqual(row["supervivencia"], 0.0,
                    f"Supervivencia negativa en {id_op} mes {row['mes']}")
                self.assertLessEqual(row["supervivencia"], 1.0,
                    f"Supervivencia >1 en {id_op} mes {row['mes']}")


class TestCLVAdicional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir_actual = os.path.dirname(os.path.abspath(__file__))
        with contextlib.redirect_stdout(StringIO()):
            cls.wrapper = CLVWrapper(cls.dir_actual)
            cls.validador = Validador()

    def test_validador_no_rompe(self):
        df = pd.read_csv(os.path.join(self.dir_actual, "parametros final.csv"))
        df_costos = pd.read_csv(os.path.join(self.dir_actual, "costos final_1.csv"))
        df_pd = pd.read_csv(os.path.join(self.dir_actual, "pd final_final_2.csv"))
        with contextlib.redirect_stdout(StringIO()):
            resultado = self.validador.validar_todo(df, df_costos, df_pd)
        self.assertTrue(resultado)

    def test_error_optimizacion_pequeno(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, _ = self.wrapper.procesar(pd.read_csv(os.path.join(self.dir_actual, "parametros final.csv")))
        for i, row in df_res.iterrows():
            self.assertLessEqual(row["error_optimizacion"], 0.05,
                f"Error de optimizacion muy alto para {row['id_operacion']}: {row['error_optimizacion']}")

    def test_clv_cercano_a_roa(self):
        with contextlib.redirect_stdout(StringIO()):
            df_res, _ = self.wrapper.procesar(pd.read_csv(os.path.join(self.dir_actual, "parametros final.csv")))
        for i, row in df_res.iterrows():
            dif = abs(row["clv_unitario"] - row["roa_target"])
            self.assertLessEqual(dif, 0.05,
                f"CLV {row['clv_unitario']} != ROA {row['roa_target']} para {row['id_operacion']}, dif={dif}")


if __name__ == "__main__":
    unittest.main()
