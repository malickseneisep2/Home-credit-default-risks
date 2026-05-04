from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
import joblib
import shap
from app.schemas import CreditApplication, PredictionResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Home Credit Default Risk API",
    description="API for credit scoring using LightGBM",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
OPTIMAL_THRESHOLD = 0.673
MODEL_PATH = "model.joblib"

# Load model
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Warning: Model not found at {MODEL_PATH}. Prediction route will fail until export_model.py is run.")
    model = None

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Home Credit API</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 2rem;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                    text-align: center;
                }
                h1 { margin-bottom: 0.5rem; }
                p { opacity: 0.8; }
                .btn {
                    display: inline-block;
                    margin-top: 1rem;
                    padding: 10px 20px;
                    background: #4facfe;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: 0.3s;
                }
                .btn:hover { background: #00f2fe; transform: translateY(-2px); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏠 Home Credit Default Risk API</h1>
                <p>Advanced Scoring System Powered by LightGBM</p>
                <p>Status: <span style="color: #4cd137;">Active</span></p>
                <a href="/docs" class="btn">View API Documentation</a>
            </div>
        </body>
    </html>
    """

@app.post("/predict", response_model=PredictionResponse)
async def predict(application: CreditApplication):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Ensure model.joblib exists.")

    # Convert Pydantic model to DataFrame
    data_dict = application.model_dump()
    df = pd.DataFrame([data_dict])
    
    # Ensure column order matches training to avoid warnings
    # (The model was trained on the order in export_model.py)

    # Prediction
    try:
        # We need the preprocessed data for SHAP
        preprocessor = model.named_steps['preprocessor']
        classifier = model.named_steps['classifier']
        
        # Transform data
        X_transformed = preprocessor.transform(df)
        
        # Conversion en format dense si c'est une matrice creuse (sparse matrix)
        if hasattr(X_transformed, "toarray"):
            X_transformed = X_transformed.toarray()
        
        # Proba
        proba = classifier.predict_proba(X_transformed)[0, 1]
        
        # SHAP (Optimisé pour Render RAM)
        explainer = shap.TreeExplainer(classifier)
        # check_additivity=False réduit la charge CPU/RAM
        shap_values = explainer.shap_values(X_transformed, check_additivity=False)
        
        # Gestion des sorties SHAP (LGBM peut renvoyer une liste ou un array)
        if isinstance(shap_values, list):
            # On prend les contributions pour la classe 1 (risque)
            contribs = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        else:
            # Si c'est un seul array, on prend la ligne correspondante
            contribs = shap_values[0] if len(shap_values.shape) > 1 else shap_values

        # Get feature names
        try:
            feature_names = preprocessor.get_feature_names_out()
        except:
            # Fallback for older sklearn
            feature_names = [f"feature_{i}" for i in range(X_transformed.shape[1])]
            
        feat_importances = dict(zip(feature_names, [float(c) for c in contribs]))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

    # Decision based on business threshold
    decision = 1 if proba >= OPTIMAL_THRESHOLD else 0
    decision_text = "Refusal (High Risk)" if decision == 1 else "Approval (Low Risk)"

    return {
        "probability": float(proba),
        "decision": int(decision),
        "decision_text": decision_text,
        "threshold": OPTIMAL_THRESHOLD,
        "feature_importance": feat_importances
    }

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}
