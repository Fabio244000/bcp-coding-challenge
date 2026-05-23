from fastapi import FastAPI

app = FastAPI(
    title='CLV Rate Optimizer API',
    description='Optimal interest rate (TEA) calculation based on Customer Lifetime Value model',
    version='1.0.0',
)


@app.get('/health')
def health():
    return {'status': 'ok'}
