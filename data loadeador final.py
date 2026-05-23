import pandas as pd
import numpy as np
import math
import os

# variables globales otra vez
g_ruta_datos = "."
g_contador_lecturas = 0

class DataLoader:
    def __init__(self, ruta="."):
        self.ruta = ruta
        self.df_c = None
        self.df_t = None
        self.df_p = None
        self.df_pr = None
        coso1 = pd.read_csv(os.path.join(ruta, "costos final_1.csv"))
        coso2 = pd.read_csv(os.path.join(ruta, "transferencia final_final.csv"))
        coso3 = pd.read_csv(os.path.join(ruta, "pd final_final_2.csv"))
        self.df_c = coso1
        self.df_t = coso2
        self.df_p = coso3

    def cargar_costos(self):
        import pandas as pd
        import os
        global g_contador_lecturas
        g_contador_lecturas = g_contador_lecturas + 1
        x = pd.read_csv(os.path.join(self.ruta, "costos final_1.csv"))
        return x

    def cargar_transferencia(self):
        import pandas as pd
        import os
        global g_contador_lecturas
        g_contador_lecturas = g_contador_lecturas + 1
        x = pd.read_csv(os.path.join(self.ruta, "transferencia final_final.csv"))
        return x

    def cargar_pd(self):
        import pandas as pd
        import os
        global g_contador_lecturas
        g_contador_lecturas = g_contador_lecturas + 1
        x = pd.read_csv(os.path.join(self.ruta, "pd final_final_2.csv"))
        return x

    def cargar_parametros(self):
        import pandas as pd
        import os
        global g_contador_lecturas
        g_contador_lecturas = g_contador_lecturas + 1
        x = pd.read_csv(os.path.join(self.ruta, "parametros final.csv"))
        return x
