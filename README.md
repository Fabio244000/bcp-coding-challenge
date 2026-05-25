# CLV Rate Optimizer API

API REST para el cálculo óptimo de tasa de interés (TEA) basado en el modelo de Customer Lifetime Value (CLV), construida con FastAPI y Arquitectura Hexagonal.

## Requisitos

- Python 3.12+

## Instalación y ejecución

### Linux / macOS

```bash
# 1. Clonar el repositorio
git clone https://github.com/Fabio244000/bcp-coding-challenge.git
cd bcp-coding-challenge

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Crear archivo de configuración
cp .env.example .env

# 4. Levantar la API
uvicorn main:app --reload
```

### Windows (PowerShell)

```powershell
# 1. Clonar el repositorio
git clone https://github.com/Fabio244000/bcp-coding-challenge.git
cd bcp-coding-challenge

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Crear archivo de configuración
Copy-Item .env.example .env

# 4. Levantar la API
uvicorn main:app --reload
```

Los valores por defecto de `.env.example` funcionan sin modificación. Ver la sección [Configuración](#configuración) si se necesita ajustar algún parámetro.

La API queda disponible en: http://localhost:8000

Documentación Swagger: http://localhost:8000/docs

## Tests

```bash
pytest tests/
```

## Configuración

Los parámetros del modelo se controlan vía el archivo `.env` en la raíz del proyecto (nunca se sube al repositorio). El archivo `.env.example` incluye todos los valores por defecto:

| Variable | Default | Descripción |
|---|---|---|
| `TEA_MIN` | `0.01` | Límite inferior de búsqueda de TEA |
| `TEA_MAX` | `0.8` | Límite superior de búsqueda de TEA |
| `TOLERANCE` | `0.000001` | Tolerancia de convergencia del optimizador |
| `MAX_ITERATIONS` | `100` | Máximo de iteraciones de Brent |
| `DAYS_PER_MONTH` | `30` | Días por mes para la curva de fondeo |
| `DATA_PATH` | `data` | Directorio de archivos CSV |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

---

## Endpoints

### GET /health

Verifica que el servicio y sus dependencias estén disponibles.

**Response 200**
```json
{
    "success": true,
    "data": { "status": "ok", "message": "Service is healthy" }
}
```

**Response 503** — parámetros de mercado no disponibles
```json
{
    "success": false,
    "message": "Service is not ready — dependencies failed to load"
}
```

---

### POST /calcular

Calcula la TEA óptima para una operación crediticia individual. Devuelve la TEA, el CLV unitario y las curvas de amortización mensuales.

**Request**
```json
{
    "product": "Credito",
    "currency": "PEN",
    "amount": 10000.0,
    "term_months": 12,
    "target_roa": 0.05
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `product` | string | `Credito`, `Leasing`, `Tarjeta` |
| `currency` | string | `PEN`, `USD` |
| `amount` | float | Monto del crédito (mayor a 0) |
| `term_months` | int | Plazo en meses (mayor a 0) |
| `target_roa` | float | ROA objetivo del banco (mayor a 0) |

**Response 200**
```json
{
    "success": true,
    "data": {
        "tea": 0.187432,
        "unit_clv": 0.050001,
        "optimization_error": 0.000001,
        "curves": [
            {
                "month": 0,
                "balance": 10000.0,
                "payment": 0.0,
                "marginal_pd": 0.0,
                "survival": 1.0,
                "funding_cost": 0.0,
                "maintenance_cost": 0.0,
                "net_flow": -10200.0,
                "discount_factor": 1.0,
                "present_value": -10200.0
            },
            {
                "month": 1,
                "balance": 9290.45,
                "payment": 932.18,
                "marginal_pd": 0.005,
                "survival": 0.995,
                "funding_cost": 38.71,
                "maintenance_cost": 11.61,
                "net_flow": 878.52,
                "discount_factor": 0.996,
                "present_value": 875.04
            }
        ]
    }
}
```

**Errores**

| Código | Causa |
|---|---|
| 404 | Producto o moneda no encontrada en los parámetros de mercado |
| 422 | Parámetros de entrada inválidos (monto negativo, plazo cero, etc.) |
| 500 | El optimizador no convergió dentro del rango configurado |
| 503 | Parámetros de mercado no disponibles |

---

### POST /calcular/lote

Calcula la TEA óptima para múltiples operaciones en una sola llamada. Devuelve TEA, CLV y error de optimización por operación (sin curvas).

**Request**
```json
[
    { "product": "Credito", "currency": "PEN", "amount": 10000.0, "term_months": 12, "target_roa": 0.05 },
    { "product": "Leasing", "currency": "USD", "amount": 50000.0, "term_months": 24, "target_roa": 0.06 }
]
```

**Response 200**
```json
{
    "success": true,
    "data": [
        { "tea": 0.187432, "unit_clv": 0.050001, "optimization_error": 0.000001 },
        { "tea": 0.213845, "unit_clv": 0.060002, "optimization_error": 0.000002 }
    ]
}
```

---

## Arquitectura

El proyecto sigue **Arquitectura Hexagonal (Puertos y Adaptadores)**. El dominio no depende de ningún adaptador — no sabe si los parámetros vienen de CSV, base de datos o API externa.

```
app/
├── config.py                   # Configuración vía pydantic-settings (.env)
├── domain/
│   ├── entities/               # LoanOperation, OptimizationResult, enums
│   ├── ports/                  # RateCalculatorPort, MarketParametersPort (interfaces)
│   ├── services/
│   │   ├── operation_validator.py    # Validación de parámetros de entrada
│   │   ├── amortization_calculator.py # Cuota y saldos (amortización francesa)
│   │   ├── clv_calculator.py         # CLV, optimización con Brent, curvas
│   │   └── rate_optimizer_service.py # Orquestador principal
│   └── exceptions.py           # Excepciones de dominio
└── adapters/
    ├── csv/                    # Carga de parámetros desde archivos CSV
    └── api/                    # Rutas FastAPI, schemas Pydantic, exception handlers

data/                           # Archivos CSV de parámetros de mercado
legacy/                         # Código original entregado (solo referencia)
tests/                          # Tests unitarios e integración
```

### Flujo de una petición

```
POST /calcular
    → get_operation()        convierte request a LoanOperation (DI)
    → get_service()          obtiene el servicio desde app.state (DI)
    → RateOptimizerService   orquesta el cálculo
        → OperationValidator      valida parámetros
        → CSVParametersAdapter    obtiene costos, tasas PD (vía puerto)
        → CLVCalculator.brentq    encuentra TEA óptima (~15 iteraciones)
        → CLVCalculator.curves    construye tabla mensual vectorizada
    ← ApiResponse[OptimizationData]  con TEA, CLV y curvas
```
