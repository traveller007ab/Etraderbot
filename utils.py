import pandas as pd
import streamlit as st

def load_data(file):
    df = pd.read_csv(file)
    df.columns = [col.strip() for col in df.columns]
    if 'Time' not in df.columns:
        st.error("CSV must include a 'Time' column.")
    return df

def display_results(trades):
    if not trades:
        st.info("No trades were generated with current settings.")
        return

    st.success(f"{len(trades)} trades generated.")
    st.dataframe(trades)
