# 🏠 Home Credit Default Risk - Decision Support System

Ce projet propose un système expert complet pour le scoring crédit, conçu pour aider les institutions bancaires à évaluer le risque de défaut de paiement de manière transparente et automatisée.

## 🌐 Déploiement en ligne
- **Dashboard Décisionnel** : [Lien dashboard](https://credit-scoring-dashboard.onrender.com/)
- **API Backend (FastAPI)** : [lien API](https://home-credit-default-risks-1.onrender.com/docs)
- **CI/CD Status** : GitHub Actions est configuré pour valider chaque modification.

## 🚀 Fonctionnalités Clés
- **Scoring en temps réel** : Prédiction de probabilité via un modèle **LightGBM** optimisé.
- **Explicabilité (SHAP)** : Analyse détaillée des facteurs influençant chaque décision (transparence totale).
- **Dashboard Professionnel** : Interface Streamlit avec 3 onglets (Décision, SHAP, Profil Détaillé).
- **Seuil Métier Optimisé** : Utilisation d'un seuil de **0.673** pour équilibrer le taux d'approbation et le risque.

## 📁 Structure du Projet
- `app/` : Logique de l'API FastAPI et schémas Pydantic.
- `app.py` : Dashboard interactif Streamlit.
- `notebooks/` : Travaux d'exploration (EDA) et de modélisation.
- `tests/` : Suite de tests unitaires automatisés.
- `export_model.py` : Script d'entraînement et d'export du pipeline complet.

## 🛠️ Utilisation Locale

1. **Installation** :
   ```bash
   pip install -r requirements.txt
   ```

2. **Lancer l'API** :
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Lancer le Dashboard** :
   ```bash
   streamlit run app.py
   ```

---
*Projet réalisé dans le cadre du module Machine Learning 2 - ISE2.*
