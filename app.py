import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.supabase_client import (
    init_db, get_bankroll, update_bankroll, update_initial_bankroll,
    add_trade, close_trade, get_trades, get_trade_by_id, update_trade, update_trade_pnl, delete_trade,
    get_methods, add_method, get_stats,
    get_players, add_player, update_player, delete_player,
    export_data, import_data
)
from src.data import (
    get_teams_by_sport, get_tourneys_by_sport, get_markets_by_sport, ALL_SPORTS,
    FOOTBALL_LEAGUES, NBA_TEAMS, FOOTBALL_TEAMS
)

st.set_page_config(page_title="Sports Trader", page_icon="🎾", layout="wide")
init_db()

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* General Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
    }
    
    /* Custom Title */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
    }
    
    /* Cards */
    .card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.15);
        border-color: rgba(0, 212, 255, 0.3);
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #00d4ff;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.6);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Positive/Negative values */
    .positive { color: #00e676 !important; }
    .negative { color: #ff5252 !important; }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05);
        border-radius: 10px 10px 0 0;
        padding: 0.75rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff20, #7c3aed20) !important;
        border-color: rgba(0, 212, 255, 0.5) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Inputs */
    .stTextInput > div > div,
    .stSelectbox > div > div,
    .stNumberInput > div > div,
    .stDateInput > div > div,
    .stTextArea > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
    }
    
    .stTextInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Tables */
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 212, 255, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 212, 255, 0.5);
    }
    
    /* Trade Card */
    .trade-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .trade-card:hover {
        border-color: rgba(0, 212, 255, 0.3);
        transform: translateX(4px);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.75rem;
        }
        
        .metric-value {
            font-size: 1.25rem;
        }
        
        .card, .metric-card {
            padding: 1rem;
        }
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Info messages */
    .stInfo {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
    }
    
    .stSuccess {
        background: rgba(0, 230, 118, 0.1);
        border: 1px solid rgba(0, 230, 118, 0.3);
        border-radius: 10px;
    }
    
    .stError {
        background: rgba(255, 82, 82, 0.1);
        border: 1px solid rgba(255, 82, 82, 0.3);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def validate_pnl(trade_type: str, odds: float, stake: float, pnl: float):
    if trade_type == "back":
        max_profit = stake * (odds - 1)
    else:
        max_profit = stake * (1 - odds)
    max_loss = -stake
    return max_loss <= pnl <= max_profit

def get_open_trades_potential():
    trades = get_trades(status="open")
    total_potential = 0
    for trade in trades:
        if trade["trade_type"] == "back":
            total_potential += trade["stake"] * (trade["odds"] - 1)
        else:
            total_potential += trade["stake"] * (1 - trade["odds"])
    return total_potential

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <h2 style="margin: 0; background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🎾 Tennis Trader</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💰 Banca")
        bankroll = get_bankroll()
        potential = get_open_trades_potential()
        
        if bankroll:
            potential_bank = bankroll['current_amount'] + potential
            roi = ((bankroll['current_amount'] - bankroll['initial_amount']) / bankroll['initial_amount']) * 100
            
            st.markdown(f"""
            <div class="card" style="margin-bottom: 0.5rem;">
                <div class="metric-value" style="font-size: 2rem;">R$ {bankroll['current_amount']:.2f}</div>
                <div class="metric-label">Banca Atual</div>
            </div>
            """, unsafe_allow_html=True)
            
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Inicial</div>
                    <div style="font-weight: 600;">R$ {bankroll['initial_amount']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_meta2:
                roi_color = "#00e676" if roi >= 0 else "#ff5252"
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">ROI</div>
                    <div style="font-weight: 600; color: {roi_color};">{roi:+.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            potential_color = "#00e676" if potential >= 0 else "#ff5252"
            st.markdown(f"""
            <div style="
                padding: 0.75rem;
                background: {f'rgba(0,230,118,0.1)' if potential >= 0 else 'rgba(255,82,82,0.1)'};
                border-radius: 10px;
                border: 1px solid {f'rgba(0,230,118,0.3)' if potential >= 0 else 'rgba(255,82,82,0.3)'};
                margin-top: 0.5rem;
                text-align: center;
            ">
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6);">Potencial Aberto</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: {potential_color};">
                    R$ {potential_bank:.2f} ({potential:+.2f})
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            open_trades = get_trades(status="open")
            if open_trades:
                st.markdown(f"<div style='text-align: center; margin-top: 0.5rem; color: rgba(255,255,255,0.5); font-size: 0.85rem;'>{len(open_trades)} aposta(s) aberta(s)</div>", unsafe_allow_html=True)
            
            with st.expander("⚙️ Configurar Banca"):
                initial = st.number_input("Banca Inicial", value=bankroll['initial_amount'], step=10.0, key="initial_bank")
                current = st.number_input("Banca Atual", value=bankroll['current_amount'], step=10.0, key="current_bank")
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("💾 Salvar", use_container_width=True):
                    update_initial_bankroll(initial, current)
                    st.rerun()
                if col_btn2.button("🔄 Resetar", use_container_width=True):
                    update_initial_bankroll(initial, initial)
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 Métodos")
        methods = get_methods()
        if methods:
            for m in methods:
                st.markdown(f"""
                <div style="
                    padding: 0.5rem 0.75rem;
                    background: rgba(255,255,255,0.05);
                    border-radius: 8px;
                    margin-bottom: 0.25rem;
                    border-left: 3px solid #00d4ff;
                ">{m}</div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: rgba(255,255,255,0.4); font-size: 0.85rem;'>Nenhum método cadastrado</div>", unsafe_allow_html=True)
        
        with st.expander("➕ Novo Método"):
            new_method = st.text_input("Nome do método", key="new_method_input")
            if st.button("Adicionar Método", use_container_width=True):
                if new_method:
                    add_method(new_method)
                    st.rerun()

def render_new_trade():
    st.markdown("### ➕ Nova Entrada")
    bankroll = get_bankroll()
    
    if "selected_sport" not in st.session_state:
        st.session_state.selected_sport = "Tenis"
    if "trade_registered" not in st.session_state:
        st.session_state.trade_registered = False
    
    if st.session_state.trade_registered:
        st.toast("Entrada registrada com sucesso!", icon="✅")
        st.session_state.trade_registered = False
    
    available = bankroll['current_amount'] if bankroll else 0
    
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    
    col0, col1, col2, col3 = st.columns([1, 1, 1, 2])
    with col0:
        date = st.date_input("📅 Data", datetime.now(), key="trade_date")
    with col1:
        stake = st.number_input("💵 Stake (R$)", min_value=1.0, value=10.0, step=1.0, key="trade_stake")
    with col2:
        stake_color = "normal" if stake <= available else "inverse"
        st.metric("💳 Disponível", f"R$ {available:.2f}", delta=None if stake <= available else "Stake > Disponível", delta_color=stake_color)
    with col3:
        sport = st.selectbox("⚽ Esporte", ALL_SPORTS, index=ALL_SPORTS.index(st.session_state.selected_sport), key="sport_select")
        st.session_state.selected_sport = sport
    
    teams = get_teams_by_sport(sport)
    custom_players = get_players(sport)
    custom_player_names = [p["name"] for p in custom_players]
    all_players = sorted(set(teams + custom_player_names))
    
    tourneys = get_tourneys_by_sport(sport)
    markets = get_markets_by_sport(sport)
    
    col1, col2 = st.columns(2)
    with col1:
        if sport == "Tenis":
            player = st.selectbox("🎾 Jogador", options=[""] + all_players, key="trade_player")
            opponent = st.selectbox("👤 Adversário", options=[""] + all_players, key="trade_opponent")
        elif sport == "Futebol":
            player = st.selectbox("🏠 Time Casa", options=[""] + all_players, key="trade_player")
            opponent = st.selectbox("✈️ Time Visitante", options=[""] + all_players, key="trade_opponent")
        else:
            player = st.selectbox("🏀 Time Casa", options=[""] + all_players, key="trade_player")
            opponent = st.selectbox("🏀 Time Visitante", options=[""] + all_players, key="trade_opponent")
        tournament = st.selectbox("🏆 Competição", options=[""] + tourneys, key="trade_tournament")
    
    with col2:
        market = st.selectbox("📊 Mercado", markets, key="trade_market")
        trade_type = st.selectbox("↔️ Tipo", ["back", "lay"], key="trade_type")
        odds = st.number_input("🎯 Odds de Entrada", min_value=1.01, max_value=100.0, value=2.0, step=0.01, key="trade_odds")
    
    methods = get_methods()
    method_options = ["Nenhum"] + methods if methods else ["Nenhum"]
    method = st.selectbox("📋 Método", method_options, key="trade_method")
    notes = st.text_area("📝 Notas", key="trade_notes", height=80)
    
    st.markdown("---")
    
    if st.button("🚀 Registrar Entrada", type="primary", use_container_width=True, key="submit_trade"):
        if stake <= (bankroll['current_amount'] if bankroll else 0):
            if player and player not in teams:
                add_player(player, sport)
            if opponent and opponent not in teams:
                add_player(opponent, sport)
            
            trade_data = {
                "date": date.isoformat(),
                "tournament": tournament,
                "player": player,
                "opponent": opponent,
                "market": market,
                "trade_type": trade_type,
                "odds": odds,
                "stake": stake,
                "method": method if method != "Nenhum" else None,
                "notes": notes,
                "sport": sport
            }
            add_trade(trade_data)
            new_balance = bankroll['current_amount'] - stake
            update_bankroll(new_balance)
            
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith("trade_") or k == "sport_select"]
            for key in keys_to_delete:
                del st.session_state[key]
            
            st.session_state.trade_registered = True
            st.rerun()
        else:
            st.error("Stake maior que banca disponível!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_open_trades():
    st.markdown("### 🔓 Trades Abertos")
    trades = get_trades(status="open")
    
    if not trades:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.5);">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎾</div>
            <div>Nenhum trade aberto</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for trade in trades:
        trade_type_color = "#00e676" if trade["trade_type"] == "back" else "#ff5252"
        
        with st.expander(f"🎾 {trade['player']} vs {trade['opponent']} - {trade['market']} ({trade['trade_type'].upper()} @ {trade['odds']})"):
            col_info, col_close = st.columns([2, 1])
            
            with col_info:
                st.markdown(f"""
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.5rem;">
                    <div style="background: rgba(255,255,255,0.05); padding: 0.5rem; border-radius: 8px;">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Data</div>
                        <div style="font-weight: 500;">{trade['date']}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.05); padding: 0.5rem; border-radius: 8px;">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Torneio</div>
                        <div style="font-weight: 500;">{trade['tournament'] or 'N/A'}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.05); padding: 0.5rem; border-radius: 8px;">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Stake</div>
                        <div style="font-weight: 500;">R$ {trade['stake']:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if trade["trade_type"] == "back":
                    max_profit = trade["stake"] * (trade["odds"] - 1)
                else:
                    max_profit = trade["stake"] * (1 - trade["odds"])
                max_loss = -trade["stake"]
                
                st.markdown(f"""
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem;">
                    <div style="background: rgba(0,230,118,0.1); padding: 0.5rem; border-radius: 8px; border: 1px solid rgba(0,230,118,0.3);">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Lucro Máximo</div>
                        <div style="font-weight: 600; color: #00e676;">R$ {max_profit:.2f}</div>
                    </div>
                    <div style="background: rgba(255,82,82,0.1); padding: 0.5rem; border-radius: 8px; border: 1px solid rgba(255,82,82,0.3);">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Prejuízo Máximo</div>
                        <div style="font-weight: 600; color: #ff5252;">R$ {max_loss:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if trade["method"]:
                    st.markdown(f"<div style='margin-top: 0.5rem; padding: 0.25rem 0.75rem; background: rgba(124,58,237,0.2); border-radius: 20px; display: inline-block; font-size: 0.85rem;'>📋 {trade['method']}</div>", unsafe_allow_html=True)
            
            with col_close:
                pnl_input = st.number_input(
                    "💰 Lucro/Prejuízo (R$)",
                    min_value=float(max_loss),
                    max_value=float(max_profit),
                    value=0.0,
                    step=1.0,
                    key=f"pnl_{trade['id']}"
                )
                
                if st.button("✅ Fechar Trade", type="primary", use_container_width=True, key=f"btn_fechar_{trade['id']}"):
                    if pnl_input >= max_loss and pnl_input <= max_profit:
                        success, msg = close_trade(trade['id'], trade['odds'], trade['stake'], pnl_input)
                        if success:
                            st.success(msg)
                            st.rerun()
                
                if st.button("❌ Cancelar", use_container_width=True, key=f"btn_cancelar_{trade['id']}"):
                    success, msg = close_trade(trade['id'], trade['odds'], trade['stake'], -trade['stake'])
                    if success:
                        st.rerun()

def render_dashboard():
    st.markdown("### 📊 Dashboard")
    stats = get_stats()
    bankroll = get_bankroll()
    potential = get_open_trades_potential()
    
    if bankroll:
        roi = ((bankroll['current_amount'] - bankroll['initial_amount']) / bankroll['initial_amount']) * 100
        profit = bankroll['current_amount'] - bankroll['initial_amount']
        profit_color = "#00e676" if profit >= 0 else "#ff5252"
        roi_color = "#00e676" if roi >= 0 else "#ff5252"
        
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
            <div class="card" style="text-align: center;">
                <div class="metric-label">Banca Atual</div>
                <div class="metric-value" style="color: #00d4ff;">R$ {bankroll['current_amount']:.2f}</div>
            </div>
            <div class="card" style="text-align: center;">
                <div class="metric-label">Lucro/Prejuízo</div>
                <div class="metric-value" style="color: {profit_color};">R$ {profit:.2f}</div>
            </div>
            <div class="card" style="text-align: center;">
                <div class="metric-label">ROI</div>
                <div class="metric-value" style="color: {roi_color};">{roi:.2f}%</div>
            </div>
            <div class="card" style="text-align: center;">
                <div class="metric-label">Potencial Total</div>
                <div class="metric-value" style="color: #7c3aed;">R$ {bankroll['current_amount'] + potential:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if stats["general"]["total_trades"] == 0:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: rgba(255,255,255,0.5);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
            <div style="font-size: 1.1rem;">Registre suas operações para ver estatísticas</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("---")
    
    gen = stats["general"]
    win_rate = (gen["wins"] / gen["total_trades"] * 100) if gen["total_trades"] > 0 else 0
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        <div class="card" style="text-align: center;">
            <div class="metric-label">Total Trades</div>
            <div class="metric-value">{gen["total_trades"]}</div>
        </div>
        <div class="card" style="text-align: center;">
            <div class="metric-label">Wins</div>
            <div class="metric-value" style="color: #00e676;">{gen["wins"]}</div>
        </div>
        <div class="card" style="text-align: center;">
            <div class="metric-label">Losses</div>
            <div class="metric-value" style="color: #ff5252;">{gen["losses"]}</div>
        </div>
        <div class="card" style="text-align: center;">
            <div class="metric-label">Taxa de Acerto</div>
            <div class="metric-value">{win_rate:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### 📋 Por Método")
        if stats["by_method"]:
            df_method = pd.DataFrame(stats["by_method"])
            df_method["win_rate"] = (df_method["wins"] / df_method["trades"] * 100).round(1)
            df_method = df_method.sort_values("pnl", ascending=False)
            
            fig = px.bar(df_method, x="method", y="pnl", title="P/L por Método",
                        color="pnl", color_continuous_scale=["#ff5252", "#00e676"],
                        template="plotly_dark")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.05)",
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_method[["method", "trades", "wins", "win_rate", "pnl"]].rename(columns={
                "method": "Método", "trades": "Trades", "wins": "Wins", "win_rate": "Win %", "pnl": "P/L"
            }), hide_index=True, use_container_width=True)
        else:
            st.info("Adicione métodos aos trades para ver estatísticas")
    
    with col_right:
        st.markdown("#### 📊 Por Mercado")
        if stats["by_market"]:
            df_market = pd.DataFrame(stats["by_market"])
            df_market["win_rate"] = (df_market["wins"] / df_market["trades"] * 100).round(1)
            df_market = df_market.sort_values("pnl", ascending=False)
            
            fig = px.pie(df_market, values="trades", names="market", title="Distribuição por Mercado",
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_market[["market", "trades", "wins", "win_rate", "pnl"]].rename(columns={
                "market": "Mercado", "trades": "Trades", "wins": "Wins", "win_rate": "Win %", "pnl": "P/L"
            }), hide_index=True, use_container_width=True)

def render_history():
    st.markdown("### 📜 Histórico")
    trades = get_trades(status="closed")
    
    if "edit_trade_id" not in st.session_state:
        st.session_state.edit_trade_id = None
    
    if st.session_state.edit_trade_id:
        render_edit_modal()
        return
    
    col_filter1, col_filter2 = st.columns([2, 1])
    with col_filter1:
        search = st.text_input("🔍 Buscar por jogador:", placeholder="Digite o nome do jogador...")
    with col_filter2:
        filter_method = st.selectbox("📋 Filtrar por método", ["Todos"] + get_methods())
    
    if not trades:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: rgba(255,255,255,0.5);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
            <div style="font-size: 1.1rem;">Nenhum trade fechado</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    df = pd.DataFrame(trades)
    
    if search:
        df = df[df["player"].str.contains(search, case=False, na=False) | 
                 df["opponent"].str.contains(search, case=False, na=False)]
    
    if filter_method != "Todos":
        df = df[df["method"] == filter_method]
    
    if len(df) == 0:
        st.info("Nenhum trade encontrado com os filtros selecionados")
        return
    
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d/%m/%Y")
    df["roi"] = (df["pnl"] / df["stake"] * 100).round(1)
    
    for _, trade in df.iterrows():
        with st.container():
            pnl_color = "#00e676" if trade['pnl'] >= 0 else "#ff5252"
            trade_type_color = "#00e676" if trade["trade_type"] == "back" else "#ff5252"
            
            st.markdown(f"""
            <div class="trade-card">
                <div style="display: grid; grid-template-columns: 1fr 2fr 2fr 1.5fr 1fr 1.5fr auto; gap: 0.5rem; align-items: center;">
                    <div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Data</div>
                        <div style="font-weight: 600;">{trade['date']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Confronto</div>
                        <div style="font-weight: 600;">{trade['player']} vs {trade['opponent']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Mercado</div>
                        <div style="font-size: 0.9rem;">{trade['market']} <span style="color: {trade_type_color}; font-weight: 600;">({trade['trade_type'].upper()})</span></div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Odds</div>
                        <div style="font-size: 0.9rem;">{trade['odds']} → {trade['exit_odds']}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Stake</div>
                        <div style="font-weight: 600;">R$ {trade['stake']:.0f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">P/L</div>
                        <div style="font-weight: 700; font-size: 1.1rem; color: {pnl_color};">R$ {trade['pnl']:.2f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("✏️ Editar", key=f"edit_{trade['id']}", help="Editar"):
                    st.session_state.edit_trade_id = trade["id"]
                    st.rerun()
            with col_btn2:
                if st.button("🗑️ Excluir", key=f"del_{trade['id']}", help="Excluir"):
                    delete_trade(trade["id"])
                    st.success("Trade excluído!")
                    st.rerun()

def render_edit_modal():
    trade = get_trade_by_id(st.session_state.edit_trade_id)
    if not trade:
        st.session_state.edit_trade_id = None
        return
    
    st.subheader(f"Editar Trade: {trade['player']} vs {trade['opponent']}")
    
    col1, col2 = st.columns(2)
    with col1:
        edit_date = st.date_input("Data", datetime.strptime(trade["date"], "%Y-%m-%d"), key="edit_date")
        edit_player = st.text_input("Jogador", value=trade["player"] or "", key="edit_player")
        edit_opponent = st.text_input("Adversário", value=trade["opponent"] or "", key="edit_opponent")
        edit_tournament = st.text_input("Torneio", value=trade["tournament"] or "", key="edit_tournament")
    
    with col2:
        edit_market = st.selectbox("Mercado", ["Match Odds", "Over 2.5 Sets", "Under 2.5 Sets", 
                                           "Handicap +3.5 Games", "Handicap -3.5 Games",
                                           "Set Betting 2-0", "Set Betting 0-2", "Set Betting 2-1", 
                                           "Set Betting 1-2", "Outro"], index=0, key="edit_market")
        edit_type = st.selectbox("Tipo", ["back", "lay"], index=0 if trade["trade_type"] == "back" else 1, key="edit_type")
        edit_odds = st.number_input("Odds Entrada", value=float(trade["odds"]), step=0.01, key="edit_odds")
        edit_stake = st.number_input("Stake (R$)", value=float(trade["stake"]), step=1.0, key="edit_stake")
    
    if edit_type == "back":
        edit_max_profit = edit_stake * (edit_odds - 1)
    else:
        edit_max_profit = edit_stake * (1 - edit_odds)
    edit_max_loss = -edit_stake
    
    edit_pnl = st.number_input(
        f"Lucro/Prejuízo (R$)", 
        min_value=float(edit_max_loss),
        max_value=float(edit_max_profit),
        value=float(trade["pnl"]) if trade["pnl"] else 0.0, 
        step=1.0, 
        key="edit_pnl"
    )
    st.caption(f"Range: R$ {edit_max_loss:.2f} a R$ {edit_max_profit:.2f}")
    
    methods = get_methods()
    method_options = ["Nenhum"] + methods if methods else ["Nenhum"]
    current_method = trade["method"] if trade["method"] else "Nenhum"
    edit_method = st.selectbox("Método", method_options, 
                               index=method_options.index(current_method) if current_method in method_options else 0, 
                               key="edit_method")
    edit_notes = st.text_area("Notas", value=trade.get("notes", "") or "", key="edit_notes")
    
    pnl_valid = validate_pnl(edit_type, edit_odds, edit_stake, edit_pnl)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    clicked_save = col_btn1.button("Salvar Alterações", type="primary")
    clicked_cancel = col_btn2.button("Cancelar")
    clicked_delete = col_btn3.button("Excluir Trade", type="secondary")
    
    if clicked_save:
        if not pnl_valid:
            st.error(f"Lucro/Prejuízo inválido! Range: R$ {edit_max_loss:.2f} a R$ {edit_max_profit:.2f}")
        else:
            trade_data = {
                "date": edit_date.isoformat(),
                "tournament": edit_tournament,
                "player": edit_player,
                "opponent": edit_opponent,
                "market": edit_market,
                "trade_type": edit_type,
                "odds": edit_odds,
                "stake": edit_stake,
                "method": edit_method if edit_method != "Nenhum" else None,
                "notes": edit_notes
            }
            update_trade(trade["id"], trade_data)
            
            success, msg = update_trade_pnl(trade["id"], edit_pnl)
            if not success:
                st.error(msg)
                return
            
            old_pnl = trade["pnl"] if trade["pnl"] else 0
            pnl_diff = edit_pnl - old_pnl
            
            bankroll = get_bankroll()
            if bankroll:
                update_bankroll(bankroll["current_amount"] + pnl_diff)
            
            st.session_state.edit_trade_id = None
            st.success("Trade atualizado!")
            st.rerun()
    
    if clicked_cancel:
        st.session_state.edit_trade_id = None
        st.rerun()
    
    if clicked_delete:
        delete_trade(trade["id"])
        st.session_state.edit_trade_id = None
        st.success("Trade excluído!")
        st.rerun()

def render_settings():
    st.markdown("### ⚙️ Configurações")
    
    with st.expander("💾 Backup - Importar/Exportar Dados"):
        col_exp_imp1, col_exp_imp2 = st.columns(2)
        
        with col_exp_imp1:
            if st.button("📤 Exportar Dados", use_container_width=True):
                import json
                data = export_data()
                st.download_button(
                    label="📥 Baixar Backup",
                    data=json.dumps(data, indent=2),
                    file_name="tennis_trader_backup.json",
                    mime="application/json",
                    key="download_backup"
                )
        
        with col_exp_imp2:
            uploaded_file = st.file_uploader("📥 Importar Backup", type=["json"])
            if uploaded_file:
                if st.button("✅ Restaurar Dados", use_container_width=True):
                    import json
                    try:
                        data = json.load(uploaded_file)
                        import_data(data)
                        st.success("Dados restaurados com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao importar: {e}")
    
    with st.expander("👥 Gerenciar Jogadores"):
        sport_filter = st.selectbox("Filtrar por esporte", ALL_SPORTS, key="settings_sport_filter")
        
        players = get_players(sport_filter)
        
        st.markdown("#### ➕ Adicionar Jogador")
        col_add1, col_add2 = st.columns([3, 1])
        with col_add1:
            new_player_name = st.text_input("Nome do jogador", key="new_player_name")
        with col_add2:
            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
            if st.button("➕ Adicionar", key="add_player_btn", use_container_width=True):
                if new_player_name:
                    if add_player(new_player_name, sport_filter):
                        st.success(f"Jogador '{new_player_name}' adicionado!")
                        st.rerun()
                    else:
                        st.error("Jogador já existe!")
        
        st.markdown("---")
        st.markdown("#### 📋 Jogadores Cadastrados")
        
        if players:
            for player in players:
                col_p1, col_p2, col_p3 = st.columns([4, 2, 1])
                with col_p1:
                    st.write(f"**{player['name']}**")
                with col_p2:
                    st.caption(player['sport'])
                with col_p3:
                    if st.button("X", key=f"del_player_{player['id']}"):
                        delete_player(player['id'])
                        st.rerun()
        else:
            st.info("Nenhum jogador cadastrado")

def main():
    render_sidebar()
    
    st.markdown('<h1 class="main-title">🎾 Tennis Trader</h1>', unsafe_allow_html=True)
    
    tabs = st.tabs([
        "📊 Dashboard", 
        "➕ Nova Entrada", 
        "🔓 Trades Abertos", 
        "📜 Histórico"
    ])
    
    with tabs[0]:
        render_dashboard()
    with tabs[1]:
        render_new_trade()
    with tabs[2]:
        render_open_trades()
    with tabs[3]:
        render_history()
    
    with st.expander("⚙️ Configurações"):
        render_settings()

if __name__ == "__main__":
    main()
