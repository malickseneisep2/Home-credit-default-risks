import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import json

# --- Configuration de la page ---
st.set_page_config(
    page_title="Home Credit Default Risk Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styles CSS personnalisés ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1e3c72;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2a5298;
        transform: translateY(-2px);
    }
    .decision-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .approved {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .refused {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar : Entrées Utilisateur ---
st.sidebar.header("📋 Informations Client")

# Vérification du statut de l'API
try:
    api_health = requests.get("http://127.0.0.1:8000/health", timeout=1)
    if api_health.status_code == 200:
        st.sidebar.success("✅ API Connectée")
    else:
        st.sidebar.warning("⚠️ API en erreur")
except:
    st.sidebar.error("❌ API Déconnectée")
    st.sidebar.info("Lancez l'API avec : `uvicorn app.main:app` dans un terminal séparé.")

st.sidebar.markdown("---")
st.sidebar.markdown("Saisissez les caractéristiques du client pour obtenir un score.")

with st.sidebar:
    st.subheader("🌐 Sources Externes")
    ext_source_1 = st.slider("EXT_SOURCE_1", 0.0, 1.0, 0.5)
    ext_source_2 = st.slider("EXT_SOURCE_2", 0.0, 1.0, 0.5)
    ext_source_3 = st.slider("EXT_SOURCE_3", 0.0, 1.0, 0.5)

    st.subheader("💰 Crédit & Revenus")
    amt_credit = st.number_input("Montant du Crédit (AMT_CREDIT)", min_value=0, value=500000)
    amt_annuity = st.number_input("Annuité (AMT_ANNUITY)", min_value=0, value=25000)
    amt_goods_price = st.number_input("Prix du bien (AMT_GOODS_PRICE)", min_value=0, value=450000)
    
    st.subheader("👥 Profil")
    org_type = st.selectbox("Type d'organisation", [
        "Business Entity Type 3", "Self-employed", "Other", "Government", "Medicine", "Trade: type 7"
    ])
    occupation = st.selectbox("Profession", [
        "Laborers", "Sales staff", "Core staff", "Managers", "Drivers", "undefined"
    ])
    gender = st.radio("Sexe", ["M", "F", "XNA"], index=1)
    days_employed = st.number_input("Jours travaillés (DAYS_EMPLOYED)", value=-1000)
    own_car_age = st.number_input("Âge de la voiture", min_value=0, value=0)

    st.subheader("⏳ Historique")
    inst_dpd_late = st.number_input("Moyenne jours de retard (INST_DPD_LATE_MEAN)", min_value=0.0, value=0.0)
    inst_amt_pay = st.number_input("Somme paiements (INST_AMT_PAYMENT_SUM)", min_value=0.0, value=100000.0)

# --- Corps Principal ---
st.title("🏠 Home Credit Default Risk")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# Préparation du payload pour l'API
payload = {
    "ORGANIZATION_TYPE": org_type,
    "EXT_SOURCE_1": ext_source_1,
    "EXT_SOURCE_2": ext_source_2,
    "EXT_SOURCE_3": ext_source_3,
    "INST_DPD_LATE_MEAN": inst_dpd_late,
    "AMT_CREDIT": float(amt_credit),
    "INST_AMT_PAYMENT_SUM": inst_amt_pay,
    "AMT_ANNUITY": float(amt_annuity),
    "DAYS_EMPLOYED": float(days_employed),
    "POS_CNT_INSTALMENT_FUTURE_MEAN": 0.0, # Valeur par défaut
    "AMT_GOODS_PRICE": float(amt_goods_price),
    "INST_DBD_MEAN": 0.0,
    "BURO_DAYS_CREDIT_MAX": 0.0,
    "PREV_CNT_PAYMENT_MEAN": 0.0,
    "BURO_DAYS_CREDIT_ENDDATE_MAX": 0.0,
    "OCCUPATION_TYPE": occupation,
    "DAYS_ID_PUBLISH": -1000.0,
    "CC_CNT_DRAWINGS_ATM_CURRENT_MEAN": 0.0,
    "OWN_CAR_AGE": float(own_car_age),
    "CODE_GENDER": gender
}

# Bouton de prédiction
if st.sidebar.button("Analyser le Risque"):
    try:
        # Appel à l'API FastAPI
        with st.spinner("Analyse en cours..."):
            response = requests.post("http://127.0.0.1:8000/predict", json=payload)
            
        if response.status_code == 200:
            result = response.json()
            proba = result["probability"]
            decision = result["decision"]
            decision_text = result["decision_text"]
            threshold = result["threshold"]

            with col1:
                st.subheader("📊 Score de Risque")
                
                # Jauge Plotly
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = proba,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Probabilité de Défaut", 'font': {'size': 24}},
                    gauge = {
                        'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "#1e3c72"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, threshold], 'color': '#d4edda'},
                            {'range': [threshold, 1], 'color': '#f8d7da'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': threshold
                        }
                    }
                ))
                fig.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🎯 Décision Finale")
                
                if decision == 0:
                    st.markdown(f'<div class="decision-box approved">✅ ACCORDÉ<br/><span style="font-size:16px;">Risque Faible ({proba:.2%})</span></div>', unsafe_allow_html=True)
                    st.success(f"Le client présente un profil solide. La probabilité de défaut ({proba:.2%}) est inférieure au seuil de sécurité ({threshold:.2%}).")
                else:
                    st.markdown(f'<div class="decision-box refused">❌ REFUSÉ<br/><span style="font-size:16px;">Risque Élevé ({proba:.2%})</span></div>', unsafe_allow_html=True)
                    st.error(f"Attention : Le profil du client présente des indicateurs de risque élevés. La probabilité ({proba:.2%}) dépasse le seuil toléré.")

                st.info("💡 **Conseil métier** : Les sources externes (EXT_SOURCE) et l'historique de paiement sont les facteurs les plus influents dans cette décision.")

            # Détails additionnels
            with st.expander("🔍 Voir les détails techniques"):
                st.json(result)
                
        else:
            st.error(f"Erreur API ({response.status_code}) : {response.text}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Impossible de se connecter à l'API. Assurez-vous que le serveur FastAPI est lancé (uvicorn app.main:app).")
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")

else:
    # État initial
    st.info("Prêt pour l'analyse. Modifiez les paramètres dans la barre latérale et cliquez sur 'Analyser le Risque'.")
    
    # Aperçu statique pour l'esthétique
    st.image("https://images.unsplash.com/photo-1554224155-1696413565d3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", use_column_width=True, caption="Système d'aide à la décision - Home Credit")
