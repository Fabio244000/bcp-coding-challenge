# BCP Coding Challenge — CLV Rate Optimizer API

API REST para el cálculo óptimo de tasa de interés (TEA) basado en el modelo de Customer Lifetime Value (CLV), construida con FastAPI y Arquitectura Hexagonal.

## Requisitos

- Python 3.12+

## Instalación

### Ubuntu / Debian
```bash
python3 -m venv bcp-challenge-venv
source bcp-challenge-venv/bin/activate
pip install -r requirements.txt
```

### macOS (Terminal o iTerm2)
```bash
python3 -m venv bcp-challenge-venv
source bcp-challenge-venv/bin/activate
pip install -r requirements.txt
```

### Windows (Command Prompt)
```bash
python -m venv bcp-challenge-venv
bcp-challenge-venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

Con el entorno virtual activado, ejecutar desde la raíz del proyecto:

```bash
uvicorn main:app --reload
```

La API quedará disponible en: http://localhost:8000

Documentación Swagger disponible en: http://localhost:8000/docs

## Ejecución de tests

```bash
pytest tests/
```

---

## Endpoints

### GET /health

Verifica que el servicio y sus dependencias estén disponibles.

**Response 200**
```json
{
    "success": true,
    "data": {
        "status": "ok",
        "message": "Service is healthy"
    }
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

Calcula la TEA óptima para una operación crediticia individual.

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
|-------|------|-------------|
| `product` | string | Producto: `Credito`, `Leasing`, `Tarjeta` |
| `currency` | string | Moneda: `PEN`, `USD` |
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

**Response 404** — producto o moneda no encontrado
```json
{
    "success": false,
    "message": "Product or currency combination not found",
    "detail": "Credito/EUR"
}
```

**Response 422** — parámetros inválidos
```json
{
    "success": false,
    "message": "Invalid operation parameters",
    "detail": "Amount must be positive"
}
```

**Response 500** — error de optimización
```json
{
    "success": false,
    "message": "Could not find optimal TEA within configured range",
    "detail": "..."
}
```

---

### POST /calcular/lote

Calcula la TEA óptima para múltiples operaciones en una sola llamada.

**Request**
```json
[
    {
        "product": "Credito",
        "currency": "PEN",
        "amount": 10000.0,
        "term_months": 12,
        "target_roa": 0.05
    },
    {
        "product": "Leasing",
        "currency": "USD",
        "amount": 50000.0,
        "term_months": 24,
        "target_roa": 0.06
    }
]
```

**Response 200**
```json
{
    "success": true,
    "data": [
        {
            "tea": 0.187432,
            "unit_clv": 0.050001,
            "optimization_error": 0.000001
        },
        {
            "tea": 0.213845,
            "unit_clv": 0.060002,
            "optimization_error": 0.000002
        }
    ]
}
```

---

## Arquitectura

El proyecto sigue **Arquitectura Hexagonal (Puertos y Adaptadores)**:

```
app/
├── domain/
│   ├── entities/        # LoanOperation, OptimizationResult
│   ├── ports/           # RateCalculatorPort, MarketParametersPort
│   ├── services/        # RateOptimizerService (lógica de negocio)
│   └── exceptions.py    # Excepciones de dominio
└── adapters/
    ├── csv/             # Carga de parámetros desde archivos CSV
    └── api/             # Rutas FastAPI, schemas, exception handler
```

El dominio no depende de ningún adaptador. Los parámetros de mercado (costos, tasas de fondeo, probabilidades de default) se inyectan vía el puerto `MarketParametersPort`.
