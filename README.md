# 🏠 Home Credit Default Risk - Scoring System

This project provides a complete machine learning pipeline and a FastAPI service to predict credit default risk for Home Credit.

## 🌐 Déploiement en ligne
- **Dashboard Streamlit** : [Lien vers le dashboard](https://votre-app.streamlit.app)
- **API Backend (FastAPI)** : [Lien vers l'API](https://votre-api.onrender.com/docs)

## 🚀 Overview
The system uses a **LightGBM** classifier trained on historical data to predict the probability of a client encountering payment difficulties.

Key features:
- **Scikit-learn Pipeline**: Includes automated preprocessing (imputation, scaling, encoding).
- **FastAPI API**: Production-ready endpoint for real-time scoring.
- **Optimized Threshold**: Uses a business-weighted threshold (**0.673**) to balance approval rate and risk.
- **CI/CD**: Integrated GitHub Actions for automated testing.

## 📁 Project Structure
- `app/`: FastAPI application code.
- `Data/`: Raw and processed datasets (ignored by git).
- `notebooks/`: Exploratory Data Analysis and modeling experiments.
- `tests/`: Unit tests for the API.
- `export_model.py`: Script to train and export the final pipeline.

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd home-credit-default-risk
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Train the model:
   ```bash
   python export_model.py
   ```

## 🖥️ Usage

### Run the API locally
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can access the interactive documentation at `/docs`.

### Run the Dashboard (Streamlit)
Make sure the API is running, then in another terminal:
```bash
streamlit run app.py
```

### Run Tests
```bash
pytest
```

## 📊 Business Logic
The model outputs a probability. Based on business requirements, we use a threshold of **0.673**:
- Probability $\ge$ 0.673 $\rightarrow$ **Refusal** (High Risk)
- Probability $<$ 0.673 $\rightarrow$ **Approval** (Low Risk)
