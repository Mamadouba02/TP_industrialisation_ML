import pytest
import pandas as pd
from fastapi.testclient import TestClient
from api.main import app
from src.config import FEATURES

PAYLOAD = dict(age=35, anciennete=5, revenu=450000, nb_reclamations=2, montant_mensuel=25000, retards_paiement=2)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_root(client):
    assert client.get('/').json()['status'] == 'running'


def test_health(client):
    assert client.get('/health').json() == {'status': 'UP'}


def test_model_info(client):
    assert client.get('/model/info').json()['model'] == 'Random Forest'


def test_prediction(client):
    response = client.post('/predict', json=PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data['prediction'] in ('CHURN', 'NO_CHURN')
    assert 0 <= data['probability'] <= 1
    assert data['model_version'] == '1.0.0'
    assert data['duration_ms'] >= 0
    assert response.headers['X-Request-ID']
    values = pd.DataFrame([PAYLOAD], columns=FEATURES)
    expected = int(app.state.model.predict(values)[0])
    assert data['prediction'] == ('CHURN' if expected else 'NO_CHURN')


@pytest.mark.parametrize('change', [{'age': 17}, {'nb_reclamations': -1}, {'age': 35.5}, {'extra': 1}, {'revenu': -1}])
def test_invalid_input(client, change):
    assert client.post('/predict', json={**PAYLOAD, **change}).status_code == 422


def test_missing_input(client):
    assert client.post('/predict', json={}).status_code == 422


def test_metrics(client):
    client.post('/predict', json=PAYLOAD)
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'churn_predictions_total' in response.text


def test_inference_failure(client, monkeypatch):
    def fail(*args):
        raise RuntimeError('internal detail')
    monkeypatch.setattr(app.state.model, 'predict_proba', fail)
    response = client.post('/predict', json=PAYLOAD)
    assert response.status_code == 503
    assert 'internal detail' not in response.text
