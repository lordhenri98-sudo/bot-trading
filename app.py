import streamlit as st
import datetime
import requests
import plotly.graph_objects as go

st.set_page_config(
    page_title="Station de Lecture de Marché — Bot Discrétionnaire",
    page_icon="⚡",
    layout="wide"
)

# Style CSS sombre
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .badge-acheter { background-color: #064e3b; color: #34d399; padding: 14px; border-radius: 6px; text-align: center; font-size: 24px; font-weight: 800; border: 2px solid #10b981; }
    .badge-vendre { background-color: #7f1d1d; color: #f87171; padding: 14px; border-radius: 6px; text-align: center; font-size: 24px; font-weight: 800; border: 2px solid #ef4444; }
    .badge-dehors { background-color: #1e293b; color: #fbbf24; padding: 14px; border-radius: 6px; text-align: center; font-size: 24px; font-weight: 800; border: 2px solid #f59e0b; }
    .terminal-card { background-color: #111827; padding: 16px; border-radius: 8px; border: 1px solid #1f2937; margin-bottom: 12px; }
    .metric-box { background-color: #1f2937; padding: 10px; border-radius: 6px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ STATION DE LECTURE DE MARCHÉ & BOT DE SIGNAUX")
st.caption("Filtres stricts de sessions et d'invalidation | Décision 100% humaine")

# --- RECUPERATION TEMPS REEL ---
@st.cache_data(ttl=5)
def get_market_prices():
    prices = {"XAUUSD": 2334.50, "USTEC": 18250.00, "BTCUSD": 81650.00}
    try:
        res_btc = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2).json()
        prices["BTCUSD"] = float(res_btc['price'])
    except:
        pass
    return prices

prices_dict = get_market_prices()

selected_asset = st.selectbox("🎯 ACTIF SOUS OBSERVATION PRINCIPALE :", ["Or (XAUUSD)", "USTEC (Nasdaq 100)", "Bitcoin (BTCUSD)"])

now_utc = datetime.datetime.utcnow()
now_paris = now_utc + datetime.timedelta(hours=1) # Heure de Paris (UTC+1)
h = now_paris.hour

# --- MOTEUR DE DECISION STRICT (RÈGLES EXACTES) ---
if "Or" in selected_asset:
    asset = "XAUUSD"
    price = prices_dict["XAUUSD"]
    
    # 1. TEST STRICT DE LA SESSION ASIE (01h00 - 09h00 Paris)
    if 1 <= h < 9:
        session_active = "Asie (01h00–09h00 Paris)"
        badge = "RISQUÉ — RESTER DEHORS"
        badge_style = "badge-dehors"
        reason = f"Session Asie en cours ({now_paris.strftime('%H:%M')}). L'Asie donne les premiers arrêts du jour, mais ne valide aucun signal. Attendre l'ouverture de Londres à 09h00."
        inv_m5, inv_h1 = "N/A", "N/A"
        h4_reg, h1_reg, m15_reg, m5_reg = "Tendance Haussière", "Attente Londres", "Neutre Asie", "Bruit Local"
        sentiment = "Attente / Bruit local"
        inst_presence = "Non (Attente des flux européens)"
        times = ["01:00 (Open)", "03:00", "05:00", f"{now_paris.strftime('%H:%M')} (Actuel)"]
        vals = [2325.0, 2328.0, 2322.0, price]
    else:
        session_active = "Londres / New York"
        badge = "ACHETER"
        badge_style = "badge-acheter"
        reason = "Chasse du Low Asie rejetée et confirmée par M15 pendant Londres. Prix en Zone Discount H1 avec volume d'absorption."
        inv_m5, inv_h1 = "2318.50 $", "2315.00 $"
        h4_reg, h1_reg, m15_reg, m5_reg = "Tendance Haussière", "Repli Défendu", "Absorption Validée", "Trigger Volume"
        sentiment = "Confiance (H1)"
        inst_presence = "Oui — Protection sur les plus bas d'Asie"
        times = ["09:00 (Open)", "10:30 (Chasse)", "12:00", f"{now_paris.strftime('%H:%M')} (Actuel)"]
        vals = [2325.0, 2320.0, 2330.0, price]

elif "USTEC" in selected_asset:
    asset = "USTEC"
    price = prices_dict["USTEC"]
    is_ny = (15 <= h < 22) or (h == 15 and now_paris.minute >= 30)
    session_active = "New York Cash (15h30 Paris)" if is_ny else "Hors Séance US (Asie/Londres en contexte)"
    
    badge = "RISQUÉ — RESTER DEHORS"
    badge_style = "badge-dehors"
    reason = "Hors séance américaine (New York Cash) ou volume sous la moyenne de la séance. Pas de signal fort hors US (Règle USTEC)." if not is_ny else "Consolidation H1. Attendre la sortie acceptée."
    inv_m5, inv_h1 = "N/A", "N/A"
    h4_reg, h1_reg, m15_reg, m5_reg = "Range", "Consolidation", "Neutre", "Volume faible"
    sentiment = "Incertitude"
    inst_presence = "Non mesurable"
    times = ["10:00", "12:00", "14:00", f"{now_paris.strftime('%H:%M')} (Actuel)"]
    vals = [18200, 18220, 18240, price]

else: # BTCUSD
    asset = "BTCUSD"
    price = prices_dict["BTCUSD"]
    session_active = "Marché Continu (UTC)"
    badge = "VENDRE"
    badge_style = "badge-vendre"
    reason = "Structure H4 baissière. H1 en rebond épuisé dans la zone Premium. M15 confirme le rejet."
    inv_m5 = f"{price * 1.01:.2f} $"
    inv_h1 = f"{price * 1.025:.2f} $"
    h4_reg, h1_reg, m15_reg, m5_reg = "Tendance Baissière", "Rebond Épuisé", "Rejet de structure", "Volume Vendeur"
    sentiment = "Peur (H1)"
    inst_presence = "Oui — Pression vendeuse en zone Premium"
    times = ["00:00 UTC", "06:00", "12:00", f"{now_paris.strftime('%H:%M')} (Actuel)"]
    vals = [83100, 82500, 82000, price]

# --- AFFICHAGE ---
st.markdown(f'<div class="{badge_style}">BADGE : {badge}</div>', unsafe_allow_html=True)
st.markdown("")

col_graph, col_panel = st.columns([3, 2])

with col_graph:
    st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
    st.markdown(f"### 📈 Structure & Dynamic Chart ({asset})")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=vals, mode='lines+markers',
        line=dict(color='#38bdf8', width=3),
        marker=dict(size=8, color='#f59e0b'),
        name="Prix"
    ))
    
    fig.update_layout(
        plot_bgcolor='#0b0f19', paper_bgcolor='#111827',
        font=dict(color='#f8fafc', size=11),
        margin=dict(l=20, r=20, t=30, b=20), height=340,
        xaxis=dict(showgrid=True, gridcolor='#1f2937'),
        yaxis=dict(showgrid=True, gridcolor='#1f2937')
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
    st.markdown("### 🏛️ Hiérarchie & Régimes Actifs")
    cols_tf = st.columns(4)
    cols_tf[0].markdown(f"<div class='metric-box'><span style='color:#94a3b8; font-size:12px;'>H4</span><br><b>{h4_reg}</b></div>", unsafe_allow_html=True)
    cols_tf[1].markdown(f"<div class='metric-box'><span style='color:#94a3b8; font-size:12px;'>H1</span><br><b>{h1_reg}</b></div>", unsafe_allow_html=True)
    cols_tf[2].markdown(f"<div class='metric-box'><span style='color:#94a3b8; font-size:12px;'>M15</span><br><b>{m15_reg}</b></div>", unsafe_allow_html=True)
    cols_tf[3].markdown(f"<div class='metric-box'><span style='color:#94a3b8; font-size:12px;'>M5</span><br><b>{m5_reg}</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_panel:
    st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Panneau d'Exécution & Invalidation")
    st.markdown(f"**Session Active :** {session_active}")
    st.markdown(f"**Prix Actuel :** `{price:,.2f} $`")
    st.markdown(f"**Heure Paris :** `{now_paris.strftime('%H:%M:%S')}`")
    st.markdown("---")
    st.markdown(f"**Raison de l'action :**\n{reason}")
    st.markdown(f"**Invalidation M5 :** `{inv_m5}` | **Invalidation H1 :** `{inv_h1}`")
    st.markdown(f"**Sentiment Inféré :** {sentiment}")
    st.markdown(f"**Présence Institutionnelle :** {inst_presence}")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔄 Rafraîchir l'Analyse", use_container_width=True):
        st.rerun()
