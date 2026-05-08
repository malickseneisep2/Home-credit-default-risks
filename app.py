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
API_URL = "https://home-credit-default-risks-1.onrender.com" 

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

    # --- SYSTÈME DE CONNEXION PRO ---
    import streamlit.components.v1 as components
    import time
    
    # Réveil via le navigateur (invisible)
    components.html(f'<iframe src="{API_URL}/health" style="display:none; width:0; height:0; border:none;"></iframe>', height=0)

    status_placeholder = st.empty()
    api_ready = False

    # On vérifie patiemment en coulisses (pendant ~50 secondes max)
    for i in range(10):
        try:
            api_check = requests.get(f"{API_URL}/health", timeout=5)
            if api_check.status_code == 200:
                api_ready = True
                break
        except:
            pass
        status_placeholder.warning("⚠️ Connexion au système en cours...")
        time.sleep(5)

    if api_ready:
        status_placeholder.success("✅ Système Connecté")
    else:
        status_placeholder.error("❌ API Hors-ligne (Veuillez rafraîchir la page)")
    
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
            st.info("Le score est calculé sur la base de 15 variables de risque.")

    with tab2:
        st.subheader("Analyse de Transparence (SHAP)")
        
        # Dictionnaire de traduction des variables techniques en noms clairs
        friendly_names = {
            'EXT_SOURCE': 'Score de fiabilité externe',
            'AMT_GOODS_PRICE': 'Prix du bien immobilier',
            'AMT_CREDIT': 'Montant du crédit demandé',
            'AMT_ANNUITY': 'Montant des mensualités',
            'DAYS_EMPLOYED': 'Ancienneté professionnelle',
            'OWN_CAR_AGE': 'Âge du véhicule',
            'ORGANIZATION_TYPE': 'Secteur d\'activité',
            'DAYS_ID_PUBLISH': 'Ancienneté des documents',
            'INST_DPD': 'Retards de paiement passés',
            'INST_AMT_PAYMENT': 'Volume des paiements effectués',
            'CNT_INSTALMENT_FUTURE': 'Mensualités restantes',
            'DAYS_CREDIT': 'Historique bureau de crédit',
            'CODE_GENDER': 'Genre du client',
            'OCCUPATION_TYPE': 'Profession'
        }

        def clean_name(name):
            n = name.replace('num__', '').replace('cat__', '')
            for tech, clean in friendly_names.items():
                if tech in n: return clean
            return n

        # --- SYNTHÈSE NARRATIVE INTELLIGENTE ---
        st.markdown("### 📝 Synthèse de l'Analyse")

        def get_feature_value_label(feature_key, payload):
            """Retourne la valeur humainement lisible d'une variable du payload."""
            raw_key = feature_key.replace('num__', '').replace('cat__', '')
            for k in payload:
                if k in raw_key or raw_key in k:
                    val = payload[k]
                    if 'EXT_SOURCE' in k:
                        return f"{val:.2f} / 1.0"
                    elif 'DAYS_EMPLOYED' in k:
                        months = round(abs(val) / 30)
                        return f"{months} mois"
                    elif 'AMT_' in k:
                        return f"{val:,.0f} FCFA"
                    elif 'OWN_CAR_AGE' in k:
                        return f"{int(val)} ans"
                    elif 'DAYS_ID_PUBLISH' in k:
                        years = round(abs(val) / 365, 1)
                        return f"{years} ans"
                    elif isinstance(val, float):
                        return f"{val:.2f}"
                    else:
                        return str(val)
            return None

        def get_feature_interpretation(feature_key, shap_value, payload):
            """Retourne une phrase d'interprétation contextualisée pour une variable."""
            raw = feature_key.replace('num__', '').replace('cat__', '')
            val_label = get_feature_value_label(feature_key, payload)
            name = clean_name(feature_key)
            val_str = f" ({val_label})" if val_label else ""

            if shap_value > 0:  # Facteur qui augmente le risque
                if 'EXT_SOURCE' in raw:
                    return f"un **{name}** faible{val_str}, signalant une fiabilité externe insuffisante"
                elif 'DAYS_EMPLOYED' in raw:
                    return f"une **{name}** très limitée{val_str}, indiquant une instabilité professionnelle"
                elif 'INST_DPD' in raw:
                    return f"des **{name}**{val_str}, révélant des difficultés passées de remboursement"
                elif 'AMT_CREDIT' in raw:
                    return f"un **{name}** élevé{val_str}, augmentant l'exposition au risque"
                elif 'OWN_CAR_AGE' in raw:
                    return f"un **{name}** avancé{val_str}"
                else:
                    return f"un niveau défavorable de **{name}**{val_str}"
            else:  # Facteur qui diminue le risque
                if 'EXT_SOURCE' in raw:
                    return f"un **{name}** solide{val_str}, attestant d'une bonne réputation externe"
                elif 'DAYS_EMPLOYED' in raw:
                    return f"une **{name}** significative{val_str}, témoignant d'une stabilité professionnelle"
                elif 'AMT_CREDIT' in raw:
                    return f"un **{name}** raisonnable{val_str}, adapté au profil"
                elif 'INST_AMT_PAYMENT' in raw:
                    return f"un **{name}** important{val_str}, démontrant une capacité de remboursement"
                else:
                    return f"un niveau favorable de **{name}**{val_str}"

        # Tri des facteurs par impact absolu
        all_sorted = sorted(shap_data.items(), key=lambda x: abs(x[1]), reverse=True)
        risk_factors = [(k, v) for k, v in all_sorted if v > 0][:3]
        protect_factors = [(k, v) for k, v in all_sorted if v < 0][:3]

        # Contribution relative des 2 premiers facteurs
        total_abs = sum(abs(v) for _, v in all_sorted) or 1
        top2_contrib = sum(abs(v) for _, v in all_sorted[:2]) / total_abs * 100

        f1, v1 = all_sorted[0]
        f2, v2 = all_sorted[1]
        interp1 = get_feature_interpretation(f1, v1, payload)
        interp2 = get_feature_interpretation(f2, v2, payload)

        if decision == 1:
            main_sentence = (
                f"Votre demande a été **refusée** principalement en raison de {interp1}, "
                f"ainsi que de {interp2}. "
                f"Ces deux éléments représentent environ **{top2_contrib:.0f}%** de l'impact total sur votre score de risque."
            )
            protect_sentence = ""
            if protect_factors:
                p1, pv1 = protect_factors[0]
                protect_sentence = f" À noter cependant, {get_feature_interpretation(p1, pv1, payload)} constitue un point positif de votre dossier."
            extra = ""
            if len(risk_factors) >= 3:
                r3, rv3 = risk_factors[2]
                extra = f" De plus, {get_feature_interpretation(r3, rv3, payload)} pèse également sur la décision."
            full_text = f"{main_sentence}{extra}{protect_sentence}".strip()
            st.markdown(f"""
            <div style="background-color:#fff5f5; border-left:5px solid #e53e3e; border-radius:10px; padding:18px 22px; margin-bottom:15px; color:#2d3748; font-size:0.97em; line-height:1.7;">
            <span style="font-size:1.1em;">❌</span> {full_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            main_sentence = (
                f"Votre demande a été **accordée** grâce notamment à {interp1} "
                f"et à {interp2}. "
                f"Ces deux facteurs représentent environ **{top2_contrib:.0f}%** de l'impact favorable sur votre score."
            )
            vigilance = ""
            if risk_factors:
                r1_key, r1_val = risk_factors[0]
                vigilance = f" Toutefois, restez vigilant : {get_feature_interpretation(r1_key, r1_val, payload)} reste un point de surveillance."
            full_text = f"{main_sentence}{vigilance}".strip()
            st.markdown(f"""
            <div style="background-color:#f0fff4; border-left:5px solid #38a169; border-radius:10px; padding:18px 22px; margin-bottom:15px; color:#2d3748; font-size:0.97em; line-height:1.7;">
            <span style="font-size:1.1em;">✅</span> {full_text}
            </div>
            """, unsafe_allow_html=True)

        col_plot, col_text = st.columns([1.2, 1])
        with col_plot:
            sorted_shap = dict(sorted(shap_data.items(), key=lambda item: abs(item[1]), reverse=True))
            top_10 = {clean_name(k): v for k, v in list(sorted_shap.items())[:10]}
            fig_s, ax = plt.subplots(figsize=(8, 6))
            ax.barh(list(top_10.keys()), list(top_10.values()), color=['#e53e3e' if v > 0 else '#38a169' for v in top_10.values()])
            ax.invert_yaxis()
            ax.set_xlabel("Impact sur le score de risque")
            st.pyplot(fig_s)
            
        with col_text:
            st.markdown("### 🔍 Détails des Impacts")
            pos = [(k, v) for k, v in sorted_shap.items() if v > 0][:3]
            neg = [(k, v) for k, v in sorted_shap.items() if v < 0][:3]
            st.markdown("**⚠️ Facteurs de Risque :**")
            for k, v in pos: st.markdown(f'<div class="impact-box negative-impact">⬆️ <b>{clean_name(k)}</b> : augmente le risque de {v:.3f}</div>', unsafe_allow_html=True)
            st.markdown("**✅ Points Forts :**")
            for k, v in neg: st.markdown(f'<div class="impact-box positive-impact">⬇️ <b>{clean_name(k)}</b> : diminue le risque de {abs(v):.3f}</div>', unsafe_allow_html=True)

        # --- BLOC DE RECOMMANDATIONS INTELLIGENT ---
        st.markdown("---")
        st.markdown("### 💡 Recommandations Personnalisées")

        def generate_recommendations(risk_factors, protect_factors, all_sorted, decision, payload, proba, threshold):
            """Génère une liste de recommandations ciblées selon le profil du dossier."""
            recommendations = []

            for feat, val in all_sorted:
                raw = feat.replace('num__', '').replace('cat__', '')

                # --- EXT_SOURCE : scores externes faibles ---
                if 'EXT_SOURCE' in raw and val > 0:
                    src_num = raw.split('EXT_SOURCE_')[-1] if 'EXT_SOURCE_' in raw else ''
                    score_val = payload.get(f'EXT_SOURCE_{src_num}', None)
                    if score_val is not None and score_val < 0.4:
                        recommendations.append({
                            "icon": "📈",
                            "priority": "haute",
                            "titre": "Améliorer le score de crédit externe",
                            "detail": (
                                f"Votre score externe (EXT_SOURCE_{src_num} = {score_val:.2f}) est en dessous du seuil de confiance (0.40). "
                                f"Pour l'améliorer, régularisez vos éventuels incidents de paiement auprès des bureaux de crédit, "
                                f"et évitez toute nouvelle demande de crédit dans les 6 prochains mois."
                            )
                        })

                # --- DAYS_EMPLOYED : ancienneté insuffisante ---
                elif 'DAYS_EMPLOYED' in raw and val > 0:
                    months = round(abs(payload.get('DAYS_EMPLOYED', 0)) / 30)
                    if months < 12:
                        recommendations.append({
                            "icon": "💼",
                            "priority": "haute",
                            "titre": "Renforcer la stabilité professionnelle",
                            "detail": (
                                f"Votre ancienneté actuelle de {months} mois est insuffisante. "
                                f"Un minimum de 12 mois dans le même emploi est généralement requis. "
                                f"Nous vous conseillons de soumettre à nouveau votre dossier après avoir atteint au moins 1 an d'ancienneté, "
                                f"ou de fournir un contrat à durée indéterminée (CDI) comme justificatif de stabilité."
                            )
                        })

                # --- INST_DPD : retards de paiement ---
                elif 'INST_DPD' in raw and val > 0:
                    dpd_val = payload.get('INST_DPD_LATE_MEAN', 0)
                    if dpd_val > 0:
                        recommendations.append({
                            "icon": "⏱️",
                            "priority": "haute",
                            "titre": "Régulariser les retards de paiement",
                            "detail": (
                                f"Un retard moyen de {dpd_val:.1f} jours a été détecté sur vos paiements passés. "
                                f"Régularisez tous les impayés en cours et maintenez un historique de paiement ponctuel "
                                f"pendant au moins 6 mois consécutifs avant de soumettre une nouvelle demande."
                            )
                        })

                # --- AMT_CREDIT trop élevé vs revenus ---
                elif 'AMT_CREDIT' in raw and val > 0:
                    amt = payload.get('AMT_CREDIT', 0)
                    annuity = payload.get('AMT_ANNUITY', 0)
                    ratio = annuity / amt if amt > 0 else 0
                    if ratio > 0.06:
                        recommendations.append({
                            "icon": "💰",
                            "priority": "moyenne",
                            "titre": "Réduire le montant du crédit demandé",
                            "detail": (
                                f"Le ratio annuité/crédit de {ratio:.1%} dépasse le seuil recommandé de 6%. "
                                f"Envisagez de réduire le montant du crédit de {amt:,.0f} FCFA ou d'allonger la durée de remboursement "
                                f"pour abaisser les mensualités et améliorer votre taux d'effort."
                            )
                        })

                # --- OWN_CAR_AGE ---
                elif 'OWN_CAR_AGE' in raw and val > 0:
                    age = payload.get('OWN_CAR_AGE', 0)
                    if age > 10:
                        recommendations.append({
                            "icon": "🚗",
                            "priority": "faible",
                            "titre": "Mise à jour du patrimoine déclaré",
                            "detail": (
                                f"L'âge avancé du véhicule déclaré ({int(age)} ans) impacte légèrement votre évaluation. "
                                f"Si vous disposez d'autres actifs récents (immobilier, épargne), veillez à les mentionner "
                                f"explicitement dans votre dossier pour renforcer votre profil patrimonial."
                            )
                        })

                # --- DAYS_ID_PUBLISH : documents anciens ---
                elif 'DAYS_ID_PUBLISH' in raw and val > 0:
                    years_id = round(abs(payload.get('DAYS_ID_PUBLISH', 0)) / 365, 1)
                    if years_id > 5:
                        recommendations.append({
                            "icon": "📄",
                            "priority": "faible",
                            "titre": "Renouveler les documents d'identité",
                            "detail": (
                                f"Vos documents d'identité datent de {years_id} ans. "
                                f"Des pièces récentes (moins de 5 ans) renforcent la crédibilité du dossier. "
                                f"Pensez à les renouveler avant de soumettre une prochaine demande."
                            )
                        })

            # Recommandation générique si peu de points actionnables
            if not recommendations:
                if decision == 1:
                    recommendations.append({
                        "icon": "🔄",
                        "priority": "moyenne",
                        "titre": "Constituer un dossier renforcé",
                        "detail": (
                            "Votre profil présente plusieurs facteurs combinés qui ont entraîné ce refus. "
                            "Nous vous recommandons de consolider votre situation financière globale sur 6 à 12 mois "
                            "(stabilité d'emploi, ponctualité des paiements, épargne constituée) puis de soumettre à nouveau votre dossier."
                        )
                    })
                else:
                    recommendations.append({
                        "icon": "✨",
                        "priority": "info",
                        "titre": "Dossier solide — Maintenir les bonnes pratiques",
                        "detail": (
                            "Votre profil est bien équilibré. Pour conserver ce niveau de fiabilité, "
                            "maintenez vos paiements à jour, évitez une accumulation de crédits simultanés, "
                            "et conservez une épargne de précaution représentant au moins 3 mois de mensualités."
                        )
                    })

            # Conseil final commun selon la proximité avec le seuil
            gap = abs(proba - threshold)
            if decision == 1 and gap < 0.05:
                recommendations.append({
                    "icon": "🎯",
                    "priority": "info",
                    "titre": "Dossier en limite de seuil",
                    "detail": (
                        f"Votre score ({proba:.2%}) est très proche du seuil d'acceptation ({threshold:.2%}). "
                        f"Une amélioration ciblée sur 1 ou 2 des points mentionnés ci-dessus pourrait suffire "
                        f"à faire basculer la décision lors d'une prochaine demande."
                    )
                })

            return recommendations[:4]  # Maximum 4 recommandations affichées

        # Couleurs et labels selon priorité
        priority_style = {
            "haute":   {"bg": "#fff5f5", "border": "#e53e3e", "badge_bg": "#e53e3e", "badge_text": "white",   "label": "Priorité haute"},
            "moyenne": {"bg": "#fffaf0", "border": "#dd6b20", "badge_bg": "#dd6b20", "badge_text": "white",   "label": "Priorité moyenne"},
            "faible":  {"bg": "#ebf8ff", "border": "#3182ce", "badge_bg": "#3182ce", "badge_text": "white",   "label": "Priorité faible"},
            "info":    {"bg": "#f0fff4", "border": "#38a169", "badge_bg": "#38a169", "badge_text": "white",   "label": "Conseil"},
        }

        reco_list = generate_recommendations(risk_factors, protect_factors, all_sorted, decision, payload, proba, threshold)

        for reco in reco_list:
            s = priority_style.get(reco["priority"], priority_style["info"])
            st.markdown(f"""
            <div style="background-color:{s['bg']}; border-left:5px solid {s['border']}; border-radius:10px;
                        padding:16px 20px; margin-bottom:12px; color:#2d3748; font-size:0.95em; line-height:1.7;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:1.3em;">{reco['icon']}</span>
                    <strong style="font-size:1.02em;">{reco['titre']}</strong>
                    <span style="margin-left:auto; background:{s['badge_bg']}; color:{s['badge_text']};
                                 font-size:0.75em; font-weight:600; padding:2px 10px; border-radius:20px;">
                        {s['label']}
                    </span>
                </div>
                <div style="padding-left:2px; color:#4a5568;">{reco['detail']}</div>
            </div>
            """, unsafe_allow_html=True)

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
    c_b.metric("Variables", "15 indicateurs")
    c_c.metric("Seuil", "0.673")
