# 🏦 Home Credit Default Risk - Système de Scoring Crédit

[![Python CI](https://github.com/malickseneisep2/Home-credit-default-risks/actions/workflows/main.yml/badge.svg)](https://github.com/malickseneisep2/Home-credit-default-risks/actions/workflows/main.yml)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://home-credit-default-risks-1.onrender.com)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit)](https://credit-scoring-dashboard.onrender.com)
[![Canva](https://img.shields.io/badge/Présentation-Canva-00C4CC?logo=canva)](VOTRE_LIEN_CANVA_ICI)

Ce projet propose une solution complète de scoring crédit pour **Home Credit**, permettant de prédire la probabilité de défaut de paiement d'un client et d'expliquer la décision de manière transparente pour les conseillers bancaires.

## 📖 Table des matières
1. [Objectif](#1-objectif)
2. [Équipe](#2-équipe)
3. [Structure du Projet](#3-structure-du-projet)
4. [Installation](#4-installation)
5. [Méthodologie](#5-méthodologie)
6. [Données](#6-données)
7. [Modèle](#7-modèle)
8. [API et Dashboard](#8-api-et-dashboard)
9. [Utilisation](#9-utilisation)
10. [Tests et CI/CD](#10-tests-et-cicd)
11. [Ressources](#11-ressources)

---

## 1. Objectif
L'objectif est de développer un algorithme de classification pour aider les décideurs financiers à accorder ou refuser un prêt. Le système ne se contente pas d'une prédiction brute, il fournit une **interprétabilité locale (SHAP)** pour justifier chaque décision, garantissant une éthique et une transparence bancaire.

## 2. Équipe
Ce projet a été réalisé par :

| Collaborateur | GitHub |
| :--- | :--- |
| **Malick SENE** | [@malickseneisep2](https://github.com/malickseneisep2) |
| **Mamady I BERETE** | [@Kefimba](https://github.com/Kefimba) |
| **Célina NGUEMFOUO NGOUMTSA** | [@nncelina](https://github.com/nncelina) |
| **Tamsir NDONG** | [@tamsir03](https://github.com/tamsir03) |

## 3. Structure du Projet
```text
├── .github/workflows/      # Automatisation CI/CD (GitHub Actions)
├── app/                    # Code source de l'API (FastAPI)
│   ├── main.py             # Point d'entrée de l'API
│   └── schemas.py          # Modèles de données Pydantic
├── tests/                  # Tests unitaires et d'intégration
├── notebooks/              # Travaux d'exploration et de modélisation
├── app.py                  # Interface Dashboard (Streamlit)
├── export_model.py         # Script d'exportation du pipeline final
├── model.joblib            # Modèle entraîné (format compressé)
├── Procfile                # Configuration du déploiement Render
└── requirements.txt        # Dépendances du projet
```

## 4. Installation
Pour installer et lancer le projet localement :

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/malickseneisep2/Home-credit-default-risks.git
   cd Home-credit-default-risks
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'API** (Local) :
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Lancer le Dashboard** (Local) :
   ```bash
   streamlit run app.py
   ```

## 5. Méthodologie
Nous avons suivi une approche MLOps rigoureuse :
*   Nettoyage des données et Feature Engineering complexe.
*   Gestion du déséquilibre des classes (SMOTE / Weight balancing).
*   Optimisation des hyperparamètres avec recherche bayésienne.
*   Industrialisation via une architecture API/Client découplée.

## 6. Données
Les données proviennent de la compétition Kaggle **Home Credit Default Risk**. Elles incluent l'historique de crédit, les données démographiques et les comportements de paiement des demandeurs. Nous avons réduit le dataset à **15 variables clés** pour optimiser l'interprétabilité et les performances en production.

## 7. Modèle
L'algorithme utilisé est un **LightGBM Classifier**, choisi pour sa rapidité et sa performance sur les données tabulaires.
*   **Seuil de décision métier** : 0.673 (optimisé pour minimiser le coût métier).
*   **Performance** : Évaluée via l'AUC et une fonction de coût métier personnalisée.

## 8. API et Dashboard
*   **API (FastAPI)** : Gère les requêtes de prédiction et calcule les valeurs SHAP en temps réel.
*   **Dashboard (Streamlit)** : Permet de saisir les données d'un client, de visualiser son risque via une jauge et de comprendre les facteurs d'influence grâce à des graphiques interactifs.

## 9. Utilisation
Une fois sur le Dashboard :
1. Renseignez les informations du client dans la barre latérale.
2. Cliquez sur "Analyser le risque".
3. Consultez la décision, le score et la synthèse narrative de l'IA.

## 10. Tests et CI/CD
Le projet intègre une suite de tests avec **Pytest** couvrant :
*   La validation des schémas d'entrée.
*   La cohérence de la logique de prédiction.
*   La disponibilité des routes API.
GitHub Actions exécute ces tests automatiquement à chaque `push` pour garantir la stabilité du déploiement.

## 11. Ressources
*   [FastAPI Documentation](https://fastapi.tiangolo.com/)
*   [Streamlit Documentation](https://docs.streamlit.io/)
*   [SHAP Documentation](https://shap.readthedocs.io/)
*   [Render Deployment](https://render.com/)
