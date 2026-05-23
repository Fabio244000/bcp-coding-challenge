# BCP Coding Challenge — CLV Rate Optimizer API

API REST para el cálculo óptimo de tasa de interés (TEA) basado en el modelo de Customer Lifetime Value (CLV), construida con FastAPI y Arquitectura Hexagonal.

## Requisitos

- Python 3.12+

## Instalación

```bash
python3 -m venv bcp-challenge-venv
source bcp-challenge-venv/bin/activate.fish  # fish shell
source bcp-challenge-venv/bin/activate       # bash/zsh
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn main:app --reload
```

Documentación disponible en: http://localhost:8000/docs
