import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from src.config import ROOT, FEATURES, VERSION

logger = logging.getLogger('churn')
logger.setLevel(logging.INFO)
logdir = Path(os.environ.get('LOG_DIR', str(ROOT / 'logs')))
logdir.mkdir(parents=True, exist_ok=True)
handler = logging.FileHandler(logdir / 'api.jsonl', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
predictions = Counter('churn_predictions_total', 'Predictions by result', ['result', 'model_version'])
latency = Histogram('churn_prediction_seconds', 'Inference duration')


@asynccontextmanager
async def lifespan(app):
    path = Path(os.environ.get('MODEL_PATH', str(ROOT / 'models/model.pkl')))
    app.state.model = joblib.load(path)
    app.state.metadata = json.loads(path.with_name('metadata.json').read_text(encoding='utf-8'))
    yield
    app.state.model = None


app = FastAPI(title='Churn Prediction API', version=VERSION, lifespan=lifespan)


class ClientData(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    age: int = Field(ge=18, le=120, strict=True)
    anciennete: int = Field(ge=0, strict=True)
    revenu: float = Field(ge=0)
    nb_reclamations: int = Field(ge=0, strict=True)
    montant_mensuel: float = Field(ge=0)
    retards_paiement: int = Field(ge=0, strict=True)


@app.middleware('http')
async def audit(request: Request, call_next):
    started = time.perf_counter()
    request.state.request_id = uuid.uuid4().hex
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers['X-Request-ID'] = request.state.request_id
        return response
    finally:
        event = {'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'level': 'ERROR' if status >= 500 else 'INFO', 'request_id': request.state.request_id, 'client': request.client.host if request.client else None, 'operation': request.url.path, 'method': request.method, 'model_version': VERSION, 'status_code': status, 'response_time_ms': round((time.perf_counter() - started) * 1000, 2)}
        logger.info(json.dumps(event))


@app.get('/')
def root():
    return {'application': app.title, 'version': VERSION, 'status': 'running'}


@app.get('/health')
def health():
    if getattr(app.state, 'model', None) is None:
        raise HTTPException(503, 'Model unavailable')
    return {'status': 'UP'}


@app.get('/model/info')
def model_info():
    return app.state.metadata


@app.post('/predict')
def predict(data: ClientData, request: Request):
    start = time.perf_counter()
    try:
        values = pd.DataFrame([data.model_dump()], columns=FEATURES)
        model = app.state.model
        prediction = int(model.predict(values)[0])
        probability = float(model.predict_proba(values)[0][list(model.classes_).index(1)])
    except Exception as exc:
        logger.error(json.dumps({'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'level': 'ERROR', 'operation': 'prediction', 'request_id': request.state.request_id, 'model_version': VERSION, 'error': 'Inference failed', 'error_type': type(exc).__name__}))
        raise HTTPException(503, 'Prediction unavailable')
    duration = time.perf_counter() - start
    result = 'CHURN' if prediction == 1 else 'NO_CHURN'
    predictions.labels(result, VERSION).inc()
    latency.observe(duration)
    logger.info(json.dumps({'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'level': 'INFO', 'operation': 'prediction', 'request_id': request.state.request_id, 'model_version': VERSION, 'result': result, 'probability': probability, 'response_time_ms': round(duration * 1000, 2)}))
    return {'prediction': result, 'probability': round(probability, 4), 'model_version': VERSION, 'duration_ms': round(duration * 1000, 2)}


Instrumentator(excluded_handlers=['/metrics']).instrument(app).expose(app)
