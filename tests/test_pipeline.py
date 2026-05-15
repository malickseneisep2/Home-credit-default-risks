import pytest
import pandas as pd
import numpy as np
import joblib
import os
from export_model import selected_features, MODEL_PATH

def test_features_list():
    """Vérifie que la liste des variables sélectionnées n'est pas vide et cohérente."""
    assert len(selected_features) > 0
    assert "EXT_SOURCE_1" in selected_features
    assert "AMT_CREDIT" in selected_features

def test_model_file_exists():
    """Vérifie que le fichier du modèle a bien été généré."""
    assert os.path.exists(MODEL_PATH), "Le fichier model.joblib est manquant. Lancez export_model.py d'abord."

def test_pipeline_loading():
    """Vérifie que l'objet chargé est bien un pipeline scikit-learn complet."""
    model = joblib.load(MODEL_PATH)
    from sklearn.pipeline import Pipeline
    assert isinstance(model, Pipeline)
    assert "preprocessor" in model.named_steps
    assert "classifier" in model.named_steps

def test_prediction_logic_on_dummy_data():
    """Vérifie que le pipeline peut traiter une ligne de donnée fictive sans planter."""
    model = joblib.load(MODEL_PATH)
    
    # Création d'une donnée de test aléatoire respectant les colonnes
    dummy_data = pd.DataFrame([{f: np.nan for f in selected_features}])
    # On remplit au moins une valeur numérique pour tester l'imputer
    dummy_data["EXT_SOURCE_2"] = 0.5
    dummy_data["ORGANIZATION_TYPE"] = "Business Entity Type 3"
    
    try:
        proba = model.predict_proba(dummy_data)
        assert proba.shape == (1, 2)
        assert 0 <= proba[0][1] <= 1
    except Exception as e:
        pytest.fail(f"Le pipeline a échoué sur des données brutes : {e}")
