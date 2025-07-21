import streamlit as st
import pandas as pd
import utils  # Your custom file management utilities

# These imports are based on your original code.
# Ensure strategy.py and trade_engine.py are in the same directory.
try:
    from strategy import FractalShiftStrategy
    from trade_engine import TradeEngine
except ImportError:
    st.error("Missing required files: 'strategy.py' or 'trade_engine.py' not found.")
    # Create dummy classes to allow the app to run without crashing
    class FractalShiftStrategy:
        def __init__(self, **kwargs): pass
        def backtest(self, df, **kwargs): return pd.DataFrame({'error': ['Strategy module not found']})
    class TradeEngine:
        def __init__(self, **kwargs): pass


def display_results(results_df):
    """
    Placeholder function to display backtest results.
    This was created because it was not part of the provided utils.py.
    You can customize this to show charts, metrics, etc.
    """
    st.subheader("Backtest Summary")
    
    if 'error' in results_df.columns:
        st.error(results_df['error'].iloc[0])
        return

    st.dataframe(results_df)

    # Display key performance indicators (KPIs) if the results contain the necessary columns
    if not results_df.empty and 'pnl' in results_df.columns:
        st.subheader("Performance Metrics")
        total_pnl = results_df['pnl'].sum()
        total_trades = len(results_df)
        winning_trades = len(results_df[results_df['pnl'] > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Net PnL", f"${total_pnl:,.2f}", delta_color=("inverse" if total_pnl < 0 else "normal"))
        col2.metric("Total Trades", total_trades)
        col3.metric("Win Rate", f"{win_rate:.2f}%")
        
        # Display a simple equity curve chart
        st.subheader("Equity Curve")
        equity_curve = results_df['pnl'].cumsum()
        st.line_chart(equity_curve)


# --- Streamlit App Layout ---

st.set_page_config(page_title="EtraderBot", layout="wide")
st.title("📊 EtraderBot — Fractal Shift Strategy")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.radio("Mode", ["Backtest", "Live"], index=0)
    symbol = st.text_input("Symbol", value="XAUUSD")
    rr_ratio = st.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0, help="The ratio of profit target to stop loss.")
    lot_size = st.number_input("Lot Size", min_value=0.01, step=0.01, value=0.13)
    max_positions = st.slider("Max Open Positions", 1, 10, 3)

    # Display file history using the utility function
    st.header("📂 File History")
    st.markdown("_Last 30 days_")
    try:
        history_df = utils.get_file_history()
        if not history_df.empty:
            st.dataframe(
                history_df[['filename', 'timestamp', 'size_mb', 'note']],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No files uploaded recently.")
    except Exception as e:
        st.error(f"Could not load file history: {e}")


# --- Main Page Content ---
if mode == "Backtest":
    st.header("📈 Backtest Mode")
    st.markdown("Upload your historical data file. ZIP files containing a single CSV are automatically extracted.")
    
    note = st.text_input("Add a note for this file (optional)", help="This note will be saved in the file history.")
    uploaded_file = st.file_uploader(
        "Upload Historical Price Data",
        type=['csv', 'zip'],
        help="Upload a CSV with price data or a ZIP containing one CSV file."
    )

    if uploaded_file:
        with st.spinner("Processing file... This may take a moment."):
            # Use the new utils function to handle the file upload, saving, and unzipping
            result_path = utils.save_uploaded_file(uploaded_file, note=note)

        # Check the result from the utility function and proceed
        if isinstance(result_path, str) and (result_path.startswith("File too large") or result_path.startswith("No CSV found")):
            st.error(result_path)
        else:
            st.success(f"File processed. Reading data from: `{result_path}`")
            try:
                # Load the data using the path returned by the utility
                df = pd.read_csv(result_path)
                
                with st.spinner("Running backtest..."):
                    strategy = FractalShiftStrategy(rr_ratio=rr_ratio)
                    results = strategy.backtest(df, lot_size=lot_size)
                
                # Display the results using the placeholder function
                display_results(results)

            except FileNotFoundError:
                st.error(f"Error: The file was not found at path: {result_path}")
            except Exception as e:
                st.error(f"An error occurred while loading data or running the backtest: {e}")

else: # Live mode
    st.header("🔴 Live Mode")
    st.warning("Live trading is not yet implemented. This feature will be available in a future version.")
    st.info("For now, please use the Backtest mode to test your strategy with historical data.")
