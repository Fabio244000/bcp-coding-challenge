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

Con el entorno virtual activado, ejecutar:

```bash
uvicorn main:app --reload
```

La API quedará disponible en: http://localhost:8000

Documentación Swagger disponible en: http://localhost:8000/docs
