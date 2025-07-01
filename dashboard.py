import streamlit as st
import pandas as pd
import sqlite3
from result_logger_supabase import get_topic_summary_supabase as get_topic_summary

st.set_page_config(page_title="📊 Performance Dashboard", layout="centered")
st.title("📊 Agentic Encore Performance Dashboard")

# Load data from SQLite
def load_results():
    conn = sqlite3.connect("data/results.db")
    df = pd.read_sql_query("SELECT * FROM results ORDER BY timestamp DESC", conn)
    conn.close()
    return df

# Display topic summary
def show_topic_summary():
    st.subheader("✅ Accuracy by Topic")
    rows = get_topic_summary()
    if rows:
        df = pd.DataFrame(rows, columns=["Topic", "Total Attempts", "Correct Answers"])
        df["Accuracy %"] = (df["Correct Answers"] / df["Total Attempts"] * 100).round(1)
        st.dataframe(df)
    else:
        st.info("No results logged yet.")

# Display full result history
def show_all_results():
    st.subheader("📋 Full Attempt History")
    df = load_results()
    if df.empty:
        st.info("No results to display.")
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(df)

# UI Options
show_topic_summary()
st.divider()
show_all_results()