import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Home Credit - Credit Scoring Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CONFIGURATION DE L'API ---
# Remplacez cette URL par votre URL Render une fois déployé
API_URL = "https://home-credit-default-risks-1.onrender.com" 
# API_URL = "http://127.0.0.1:8000" # Décommentez pour tester en local

# --- INITIALISATION DU SESSION STATE ---
if 'predicted' not in st.session_state:
    st.session_state.predicted = False
if 'api_data' not in st.session_state:
    st.session_state.api_data = None

# --- DESIGN ET CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
    }

    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
    }
    
    .status-card {
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 25px;
        border-left: 10px solid;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .approved-card { background-color: #f0fff4; border-color: #38a169; color: #2f855a; }
    .refused-card { background-color: #fff5f5; border-color: #e53e3e; color: #c53030; }

    .impact-box {
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 0.9em;
    }
    .positive-impact { background-color: #e6fffa; border: 1px solid #38a169; color: #234e52; }
    .negative-impact { background-color: #fff5f5; border: 1px solid #e53e3e; color: #742a2a; }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 10px;
        font-weight: 700;
    }
    
    .reset-btn>button {
        background: white !important;
        color: #1e3c72 !important;
        border: 1px solid #1e3c72 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR : CONFIGURATION ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80", width="stretch")
    st.title("Configuration du Dossier")
    
    # Navigation
    if st.session_state.predicted:
        st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
        if st.button("🏠 Retour à l'accueil"):
            st.session_state.predicted = False
            st.session_state.api_data = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

    # Statut API
    try:
        api_check = requests.get(f"{API_URL}/health", timeout=15)
        if api_check.status_code == 200:
            st.success("✅ Système Connecté")
        else:
            st.warning("⚠️ API Instable")
    except:
        st.error("❌ API Hors-ligne")
    
    with st.expander("👤 Profil & Identité", expanded=not st.session_state.predicted):
        gender = st.selectbox("Genre (CODE_GENDER)", ["F", "M", "XNA"], format_func=lambda x: "Femme" if x=="F" else ("Homme" if x=="M" else "Non renseigné"))
        occupation = st.selectbox("Profession", ["Laborers", "Sales staff", "Core staff", "Managers", "Drivers", "High skill tech staff", "Accountants", "undefined"])
        org_type = st.selectbox("Organisation", ["Business Entity Type 3", "Self-employed", "Other", "Government", "Medicine", "Trade: type 7"])
        days_employed = st.number_input("Jours d'emploi", value=-1500)
        days_id_publish = st.number_input("Jours ID Publish", value=-1000)

    with st.expander("💰 Finances & Crédit"):
        amt_credit = st.number_input("Montant Crédit", min_value=0, value=500000)
        amt_annuity = st.number_input("Annuité", min_value=0, value=25000)
        amt_goods_price = st.number_input("Prix du bien", min_value=0, value=450000)

    with st.expander("📊 Scores Externes"):
        ext_1 = st.slider("EXT_SOURCE_1", 0.0, 1.0, 0.5)
        ext_2 = st.slider("EXT_SOURCE_2", 0.0, 1.0, 0.5)
        ext_3 = st.slider("EXT_SOURCE_3", 0.0, 1.0, 0.5)

    with st.expander("⏳ Historique & Bureau"):
        inst_dpd_late = st.number_input("Retard moyen (DPD)", value=0.0)
        inst_amt_pay = st.number_input("Somme paiements", value=100000.0)
        buro_days_max = st.number_input("Max jours crédit Bureau", value=100.0)
        own_car_age = st.number_input("Âge de la voiture", min_value=0.0, value=0.0)
        # Valeurs complétantes
        inst_dbd_mean, pos_future_inst, buro_end_max, prev_cnt_pay, cc_draw_atm = 10.0, 12.0, 500.0, 12.0, 0.0

    st.markdown("---")
    if not st.session_state.predicted:
        predict_btn = st.button("LANCER L'ANALYSE")
    else:
        st.info("Résultats affichés. Utilisez le bouton 'Retour' pour modifier les données.")

# --- PAYLOAD ---
payload = {
    "ORGANIZATION_TYPE": org_type, "EXT_SOURCE_1": ext_1, "EXT_SOURCE_2": ext_2, "EXT_SOURCE_3": ext_3,
    "INST_DPD_LATE_MEAN": inst_dpd_late, "AMT_CREDIT": float(amt_credit), "INST_AMT_PAYMENT_SUM": inst_amt_pay,
    "AMT_ANNUITY": float(amt_annuity), "DAYS_EMPLOYED": float(days_employed), "POS_CNT_INSTALMENT_FUTURE_MEAN": float(pos_future_inst),
    "AMT_GOODS_PRICE": float(amt_goods_price), "INST_DBD_MEAN": float(inst_dbd_mean), "BURO_DAYS_CREDIT_MAX": float(buro_days_max),
    "PREV_CNT_PAYMENT_MEAN": float(prev_cnt_pay), "BURO_DAYS_CREDIT_ENDDATE_MAX": float(buro_end_max), "OCCUPATION_TYPE": occupation,
    "DAYS_ID_PUBLISH": float(days_id_publish), "CC_CNT_DRAWINGS_ATM_CURRENT_MEAN": float(cc_draw_atm), "OWN_CAR_AGE": float(own_car_age),
    "CODE_GENDER": gender
}

# --- LOGIQUE DE PRÉDICTION ---
if not st.session_state.predicted and 'predict_btn' in locals() and predict_btn:
    try:
        with st.spinner("🔄 Analyse du risque..."):
            response = requests.post(f"{API_URL}/predict", json=payload)
        if response.status_code == 200:
            st.session_state.api_data = response.json()
            st.session_state.predicted = True
            st.rerun()
        else:
            st.error(f"Erreur API ({response.status_code})")
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")

# --- HEADER PRINCIPAL ---
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    st.image("https://img.icons8.com/fluency/96/bank-building.png", width=80)
with col_title:
    st.title("Credit Scoring Dashboard")
    st.caption("Plateforme d'analyse prédictive pour l'aide à la décision bancaire")

# --- AFFICHAGE ---
if st.session_state.predicted:
    data = st.session_state.api_data
    proba, decision, threshold, shap_data = data["probability"], data["decision"], data["threshold"], data["feature_importance"]
    
    tab1, tab2, tab3 = st.tabs(["🎯 DÉCISION", "🧠 EXPLICABILITÉ (SHAP)", "👤 PROFIL DÉTAILLÉ"])
    
    with tab1:
        c1, c2 = st.columns([1, 1])
        with c1:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = proba,
                title = {'text': "Probabilité de Défaut", 'font': {'size': 20}},
                gauge = {
                    'axis': {'range': [0, 1]}, 'bar': {'color': "#1e3c72"},
                    'steps': [{'range': [0, threshold], 'color': "#e6fffa"}, {'range': [threshold, 1], 'color': "#fff5f5"}],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'value': threshold}
                }
            ))
            st.plotly_chart(fig, width="stretch")
        with c2:
            if decision == 0:
                st.markdown(f'<div class="status-card approved-card"><h2>✅ ACCORDÉ</h2><p>Risque maîtrisé : {proba:.2%}</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-card refused-card"><h2>❌ REFUSÉ</h2><p>Risque élevé : {proba:.2%}</p></div>', unsafe_allow_html=True)
            st.metric("Seuil métier", f"{threshold:.3f}")
            st.info("Le score est calculé sur la base de 20 variables de risque.")

    with tab2:
        st.subheader("Analyse de Transparence (SHAP)")
        col_plot, col_text = st.columns([1.2, 1])
        with col_plot:
            sorted_shap = dict(sorted(shap_data.items(), key=lambda item: abs(item[1]), reverse=True))
            top_10 = dict(list(sorted_shap.items())[:10])
            fig_s, ax = plt.subplots(figsize=(8, 6))
            ax.barh(list(top_10.keys()), list(top_10.values()), color=['#e53e3e' if v > 0 else '#38a169' for v in top_10.values()])
            ax.invert_yaxis()
            st.pyplot(fig_s)
        with col_text:
            st.markdown("### 🔍 Facteurs d'Influence")
            pos = [(k, v) for k, v in sorted_shap.items() if v > 0][:3]
            neg = [(k, v) for k, v in sorted_shap.items() if v < 0][:3]
            st.markdown("**⚠️ Augmentent le risque :**")
            for k, v in pos: st.markdown(f'<div class="impact-box negative-impact">⬆️ <b>{k}</b></div>', unsafe_allow_html=True)
            st.markdown("**✅ Sécurisent le dossier :**")
            for k, v in neg: st.markdown(f'<div class="impact-box positive-impact">⬇️ <b>{k}</b></div>', unsafe_allow_html=True)

    with tab3:
        st.subheader("Analyse Comparative du Client")
        r1, r2 = st.columns(2)
        
        with r1:
            # 1. Bar chart Scores Externes
            st.markdown("##### 📊 Scores Externes (vs Moyenne)")
            fig_ext = go.Figure(data=[
                go.Bar(name='Client', x=['Ext_1', 'Ext_2', 'Ext_3'], y=[ext_1, ext_2, ext_3], marker_color='#1e3c72', text=[f"{ext_1:.2f}", f"{ext_2:.2f}", f"{ext_3:.2f}"], textposition='auto'),
                go.Bar(name='Moyenne', x=['Ext_1', 'Ext_2', 'Ext_3'], y=[0.502, 0.514, 0.511], marker_color='#cbd5e0', text=["0.502", "0.514", "0.511"], textposition='auto')
            ])
            fig_ext.update_layout(barmode='group', height=300, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_ext, width="stretch")

            # 2. Loan-to-Value (LTV)
            st.markdown("##### 🏠 Ratio Crédit / Prix du Bien")
            ltv = amt_credit / amt_goods_price if amt_goods_price > 0 else 0
            fig_ltv = go.Figure(go.Indicator(
                mode = "gauge+number", value = ltv,
                gauge = {'axis': {'range': [0, 1.5]}, 'bar': {'color': "#2a5298"}, 'steps': [{'range': [0, 1], 'color': "lightgray"}]},
                domain = {'x': [0, 1], 'y': [0, 1]}
            ))
            fig_ltv.update_layout(height=250, margin=dict(t=40, b=20))
            st.plotly_chart(fig_ltv, width="stretch")

        with r2:
            # 3. Ancienneté Professionnelle
            st.markdown("##### 💼 Ancienneté (Années)")
            years = abs(days_employed) / 365
            avg_years = abs(-2384) / 365
            fig_exp = px.bar(x=['Client', 'Moyenne Globale'], y=[years, avg_years], color=['Client', 'Moyenne Globale'], color_discrete_map={'Client':'#1e3c72', 'Moyenne Globale':'#cbd5e0'})
            fig_exp.update_layout(showlegend=False, height=300, margin=dict(t=20, b=20))
            st.plotly_chart(fig_exp, width="stretch")

            # 4. Charge de remboursement
            st.markdown("##### 💳 Ratio Annuité / Crédit")
            ratio = amt_annuity / amt_credit if amt_credit > 0 else 0
            avg_ratio = 0.0537
            fig_ratio = go.Figure(go.Indicator(
                mode = "number+delta", value = ratio*100,
                delta = {'reference': avg_ratio*100, 'relative': False, 'valueformat': ".1f"},
                number = {'suffix': "%"}, title = {"text": "Taux de charge"},
            ))
            fig_ratio.update_layout(height=250)
            st.plotly_chart(fig_ratio, width="stretch")

        st.markdown("---")
        st.markdown("#### 📋 Données du Dossier")
        st.dataframe(pd.DataFrame(payload.items(), columns=['Indicateur', 'Valeur']), width="stretch")

else:
    # --- ACCUEIL ---
    st.markdown("""
    <div style="text-align: center; padding: 40px; background-color: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
        <img src="https://images.unsplash.com/photo-1554224155-1696413565d3?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" style="width: 100%; max-width: 600px; border-radius: 15px; margin-bottom: 30px;" />
        <h1 style="color: #1e3c72;">Analyseur de Risque de Crédit</h1>
        <p style="color: #718096; font-size: 1.2em; max-width: 700px; margin: 0 auto;">
            Bienvenue sur l'outil d'aide à la décision. Veuillez configurer les paramètres du client dans la barre latérale pour lancer l'analyse prédictive.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    c_a, c_b, c_c = st.columns(3)
    c_a.metric("Modèle", "LightGBM")
    c_b.metric("Variables", "20 indicateurs")
    c_c.metric("Seuil", "0.673")
