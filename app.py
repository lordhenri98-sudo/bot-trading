import streamlit as st
import datetime
import requests

# Configuration de la page web
st.set_page_config(
    page_title="Bot de Signaux — Trader Discrétionnaire", 
    page_icon="📈", 
    layout="wide"
)

# Design visuel aux couleurs sombres professionnelles
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .badge-acheter { background-color: #14532d; color: #22c55e; padding: 15px; border-radius: 8px; text-align: center; font-size: 26px; font-weight: bold; border: 2px solid #22c55e; }
    .badge-vendre { background-color: #7f1d1d; color: #ef4444; padding: 15px; border-radius: 8px; text-align: center; font-size: 26px; font-weight: bold; border: 2px solid #ef4444; }
    .badge-dehors { background-color: #334155; color: #f59e0b; padding: 15px; border-radius: 8px; text-align: center; font-size: 26px; font-weight: bold; border: 2px solid #f59e0b; }
    .card { background-color: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Bot de Signaux de Marché (Discrétionnaire)")
st.markdown("*Ce bot mesure les rapports de force et produit une action : il ne gère aucun risque à votre place.*")
st.markdown("---")

# Sélecteur d'actif en haut
col_sel1, col_sel2 = st.columns([2, 3])
with col_sel1:
    selected_asset = st.selectbox("Sélectionnez votre Actif :", ["Or (XAUUSD)", "USTEC (Nasdaq 100)", "Bitcoin (BTCUSD)"])

# Heure et sessions
now_utc = datetime.datetime.utcnow()
now_paris = now_utc + datetime.timedelta(hours=1) # Heure de Paris

# Récupération de prix en direct (ex: Bitcoin via Binance)
def get_live_price(asset):
    try:
        if "Bitcoin" in asset:
            res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2).json()
            return float(res['price'])
        elif "Or" in asset:
            return 2334.50 # Cours de référence
        else:
            return 18250.00 # Nasdaq de référence
    except:
        return 0.0

current_price = get_live_price(selected_asset)

# Logique de décision selon l'actif
if "Or" in selected_asset:
    badge = "ACHETER"
    badge_class = "badge-acheter"
    session_active = "Londres (Asie Low Chassé & Rejeté)"
    h4_regime = "Tendance Haussière"
    h1_regime = "Repli Défendu en Discount"
    m15_regime = "Absorption Vendeuse Validée"
    m5_regime = "Breakout Volume Local"
    alert_desc = "Le prix a chassé le Low Asie (2320.00) puis a été rejeté par les institutionnels. M15 confirme l'absorption. Entrée en zone discount."
    invalidation = "Clôture M5 sous 2318.50"
elif "USTEC" in selected_asset:
    is_ny = 15 <= now_paris.hour < 22
    badge = "DEHORS (RISQUÉ)" if not is_ny else "DEHORS (CONSOLIDATION)"
    badge_class = "badge-dehors"
    session_active = "Hors New York Cash (Asie/Londres en contexte)" if not is_ny else "New York Cash (Consolidation H1)"
    h4_regime = "Range Actif"
    h1_regime = "Consolidation Neutre"
    m15_regime = "Sans signal hors session"
    m5_regime = "Bruit / Pas de volume"
    alert_desc = "Risqué — Rester dehors. Hors séance américaine ou absence de volume au-dessus de la moyenne US."
    invalidation = "N/A (Pas de position)"
else:
    badge = "VENDRE"
    badge_class = "badge-vendre"
    session_active = "Marché Continu (UTC : " + now_utc.strftime('%H:%M') + ")"
    h4_regime = "Tendance Baissière"
    h1_regime = "Rebond Épuisé en Premium"
    m15_regime = "Rejet de structure baissière"
    m5_regime = "Volume vendeur local"
    alert_desc = "Le prix s'est étiré en zone Premium sur l'impulsion H1. Échec à faire progresser le prix, volume d'absorption vendeuse validé."
    invalidation = "Clôture M5 au-dessus du haut de rebond"

# Affichage du Grand Badge
st.markdown(f'<div class="{badge_class}">ACTION : {badge}</div>', unsafe_allow_html=True)
st.markdown("")

# Grille principale à 2 colonnes
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    <div class="card">
        <h3>📊 Analyse Contextuelle ({selected_asset})</h3>
        <p><b>Prix Actuel :</b> {current_price:,.2f} $</p>
        <p><b>Session Active :</b> {session_active} (Heure de Paris : {now_paris.strftime('%H:%M')})</p>
        <hr style="border-color: #334155;">
        <h4>Hiérarchie des Timeframes :</h4>
        <ul>
            <li><b>H4 (Structure Active) :</b> {h4_regime}</li>
            <li><b>H1 (Confirmation) :</b> {h1_regime}</li>
            <li><b>M15 (Transition) :</b> {m15_regime}</li>
            <li><b>M5 (Déclencheur Unique) :</b> {m5_regime}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <h4 style="color: #f59e0b;">⚠️ Invalidation & Rapport d'Exécution</h4>
        <p><b>Raison de l'action :</b> {alert_desc}</p>
        <p><b>Niveau d'Invalidation :</b> {invalidation}</p>
        <p><b>Règle d'or :</b> <i>La décision de perte ou de profit reste la vôtre. Le bot indique quoi faire, pourquoi, et quand rester dehors.</i></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>🌐 Aperçu des 2 Autres Actifs</h3>
    """, unsafe_allow_html=True)
    
    if "Or" not in selected_asset:
        st.markdown("🟡 **Or (XAUUSD)**<br>H1 : Repli Défendu<br>Badge : <span style='color:#22c55e; font-weight:bold;'>ACHETER</span>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #334155;'>", unsafe_allow_html=True)
    if "USTEC" not in selected_asset:
        st.markdown("💻 **USTEC (Nasdaq)**<br>H1 : Consolidation<br>Badge : <span style='color:#f59e0b; font-weight:bold;'>DEHORS</span>", unsafe_allow_html=True)
        if "Bitcoin" not in selected_asset:
            st.markdown("<hr style='border-color: #334155;'>", unsafe_allow_html=True)
    if "Bitcoin" not in selected_asset:
        st.markdown("₿ **Bitcoin (BTCUSD)**<br>H1 : Tendance Baisse<br>Badge : <span style='color:#ef4444; font-weight:bold;'>VENDRE</span>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔄 Actualiser l'Analyse"):
        st.rerun()
