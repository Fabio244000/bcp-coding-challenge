COSTS_FILE = 'costos final_1.csv'
RATES_FILE = 'transferencia final_final.csv'
PD_FILE  = 'pd final_final_2.csv'

COSTS_COLUMNS = {
    'producto': 'product',
    'moneda': 'currency',
    'costo_originacion_pct': 'origination_cost',
    'costo_mantenimiento_anual_pct': 'maintenance_cost',
}

RATES_COLUMNS = {
    'producto': 'product',
    'moneda': 'currency',
    'plazo_dias': 'term_days',
    'tasa_anual': 'annual_rate',
}

PD_COLUMNS = {
    'producto': 'product',
    'mes': 'month',
    'pd_marginal': 'marginal_pd',
}