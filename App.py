import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timedelta

# --- USER SETTINGS ---
st.set_page_config(page_title="Fractal Shift Bot", layout="wide")

# Sidebar Config
st.sidebar.title("⚙️ Bot Settings")
def_symbol = st.sidebar.text_input("Default Symbol", value="XAUUSD")
trade_mode = st.sidebar.radio("Trade Mode", ["Live", "Backtest"], index=1)
risk_reward_ratio = st.sidebar.slider("Risk/Reward Ratio", 0.5, 5.0, 2.0)
max_open_trades = st.sidebar.checkbox("Allow Multiple Trades", value=True)

# --- BACKTEST MODE ---
if trade_mode == "Backtest":
    st.title("📊 Fractal Shift Backtest Mode")
    uploaded_file = st.file_uploader("Upload Historical Price Data (.csv)")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)

        st.success(f"Loaded {len(df)} rows of data.")

        signals = []
        equity = 1000
        balance = equity
        risk_per_trade = 0.01 * balance
        wins, losses = 0, 0
        equity_curve = [equity]

        for i in range(10, len(df)):
            fractal_high = max(df['high'].iloc[i-5:i])
            fractal_low = min(df['low'].iloc[i-5:i])
            current_close = df['close'].iloc[i]

            if current_close > fractal_high:
                entry = current_close
                stop = df['low'].iloc[i-1]
                target = entry + (entry - stop) * risk_reward_ratio

                result_slice = df.iloc[i:i+10]
                hit_tp = any(result_slice['high'] >= target)
                hit_sl = any(result_slice['low'] <= stop)

                if hit_tp:
                    equity += risk_per_trade * risk_reward_ratio
                    wins += 1
                    result = "TP"
                elif hit_sl:
                    equity -= risk_per_trade
                    losses += 1
                    result = "SL"
                else:
                    result = "No Outcome"

                equity_curve.append(equity)

                signals.append({
                    "time": df.index[i],
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "result": result
                })

        st.subheader("📈 Results")
        st.write(f"Final Equity: ${equity:.2f}")
        st.write(f"Win Rate: {(wins / (wins + losses)) * 100:.2f}%" if (wins + losses) > 0 else "No Trades")
        st.write(f"Trades: {wins + losses} (W: {wins} / L: {losses})")

        st.line_chart(pd.DataFrame({"Equity": equity_curve}))
        st.dataframe(pd.DataFrame(signals))

# --- LIVE MODE ---
else:
    st.title("🤖 Fractal Shift Bot - Live Trading Mode")

    st.subheader("🔐 MT5 Login")
    login = st.text_input("Login")
    password = st.text_input("Password", type="password")
    server = st.text_input("Server")
    login_button = st.button("Login to MT5")

    if login_button:
        connected = mt5.initialize(login=int(login), server=server, password=password)
        if connected:
            st.success("Successfully connected to MT5 broker.")
        else:
            st.error("Failed to connect to MT5. Please check credentials and try again.")

    if mt5.initialize():
        st.info("Connection already active.")
        # Add live trading logic here
    else:
        st.warning("Please login to MT5 to enable live trading.")
