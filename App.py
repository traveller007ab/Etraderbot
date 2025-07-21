import streamlit as st
from strategy import FractalShiftStrategy
from trade_engine import TradeEngine
from utils import load_data, display_results

st.set_page_config(page_title="EtraderBot", layout="wide")
st.title("📊 EtraderBot — Fractal Shift Strategy")

# Sidebar settings
mode = st.sidebar.radio("Mode", ["Backtest", "Live"], index=0)
symbol = st.sidebar.text_input("Symbol", value="XAUUSD")
rr_ratio = st.sidebar.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0)
lot_size = st.sidebar.number_input("Lot Size", min_value=0.13, step=0.01, value=0.13)
max_positions = st.sidebar.slider("Max Open Positions", 1, 10, 3)

if mode == "Backtest":
    uploaded_file = st.file_uploader("Upload Historical Price Data (.csv)")
    if uploaded_file:
        df = load_data(uploaded_file)
        strategy = FractalShiftStrategy(rr_ratio=rr_ratio)
        results = strategy.backtest(df, lot_size=lot_size)
        display_results(results)

else:
    st.warning("Live mode will be supported in the hosted version. For now, use Backtest.")
