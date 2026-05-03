from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Home Credit Default Risk API" in response.text

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_prediction_endpoint():
    # Payload d'exemple
    payload = {
        "ORGANIZATION_TYPE": "Business Entity Type 3",
        "EXT_SOURCE_1": 0.08,
        "EXT_SOURCE_2": 0.26,
        "EXT_SOURCE_3": 0.13,
        "AMT_CREDIT": 406597.5,
        "DAYS_EMPLOYED": -637.0,
        "CODE_GENDER": "M"
    }
    response = client.post("/predict", json=payload)
    
    # Si le modèle est chargé, on vérifie la structure de la réponse
    if response.status_code == 200:
        data = response.json()
        assert "probability" in data
        assert "decision" in data
        assert "decision_text" in data
    else:
        # Si le modèle n'est pas chargé (ex: dans GitHub Actions sans export_model),
        # l'API doit renvoyer une erreur 503 gérée
        assert response.status_code == 503

def test_invalid_data():
    # On envoie une chaîne au lieu d'un nombre pour EXT_SOURCE_1
    payload = {
        "EXT_SOURCE_1": "pas_un_nombre"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422 # Unprocessable Entity (Erreur de validation Pydantic)

def test_default_values():
    # Test avec un payload minimal pour vérifier les valeurs par défaut de Pydantic
    payload = {
        "EXT_SOURCE_2": 0.5
    }
    response = client.post("/predict", json=payload)
    if response.status_code == 200:
        data = response.json()
        assert "probability" in data
    else:
        assert response.status_code == 503

def test_prediction_logic():
    # Vérifie que la décision suit bien le seuil de 0.673
    # Note: On ne peut tester ça que si le modèle est chargé
    payload = {
        "EXT_SOURCE_1": 0.01,
        "EXT_SOURCE_2": 0.01,
        "EXT_SOURCE_3": 0.01
    }
    response = client.post("/predict", json=payload)
    if response.status_code == 200:
        data = response.json()
        proba = data["probability"]
        decision = data["decision"]
        threshold = data["threshold"]
        
        expected_decision = 1 if proba >= threshold else 0
        assert decision == expected_decision
        assert threshold == 0.673

def test_cors_headers():
    # Vérifie que les headers CORS sont présents (important pour le frontend)
    response = client.options("/predict", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
