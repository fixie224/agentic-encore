import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import sys, os

# Fix import path if run from pages/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from result_logger_supabase import get_topic_summary_supabase

st.set_page_config(page_title="📊 Performance Dashboard", layout="centered")
st.title("📊 ENCOR Quiz Performance Dashboard")

# --- Date Filter ---
st.markdown("### 🗓️ Filter by Time Range")
option = st.selectbox("Show results from:", ["All Time", "Last 7 Days", "Last 30 Days"])

def filter_summary(data):
    if option == "All Time":
        return data
    limit_days = 7 if option == "Last 7 Days" else 30
    cutoff = datetime.datetime.now() - datetime.timedelta(days=limit_days)
    return [row for row in data if datetime.datetime.fromisoformat(row['timestamp']) >= cutoff]

# --- Load + Filter ---
raw = get_topic_summary_supabase(raw=True)
data = filter_summary(raw)

if not data:
    st.warning("⚠️ No data available for selected range. Try taking more quizzes.")
    st.stop()

# --- Summary Table ---
df = pd.DataFrame(data)
summary = df.groupby("topic").agg(
    total=("is_correct", "count"),
    correct=("is_correct", "sum")
).reset_index()
summary["Accuracy (%)"] = (summary["correct"] / summary["total"] * 100).round(1)

st.dataframe(summary.rename(columns={"topic": "Topic"}), use_container_width=True)

# --- Top & Bottom Performance ---
st.markdown("---")
st.subheader("🥇 Top & Bottom Performance")
top = summary.sort_values("Accuracy (%)", ascending=False).head(1)
bottom = summary.sort_values("Accuracy (%)").head(1)

st.success(f"✅ Best Topic: **{top['topic'].values[0]}** ({top['Accuracy (%)'].values[0]}%)")
st.error(f"⚠️ Weakest Topic: **{bottom['topic'].values[0]}** ({bottom['Accuracy (%)'].values[0]}%)")

# --- Chart: Accuracy by Topic ---
st.markdown("---")
st.subheader("✅ Accuracy by Topic")
fig, ax = plt.subplots()
ax.barh(summary["topic"], summary["Accuracy (%)"], color="skyblue")
ax.set_xlabel("Accuracy (%)")
ax.set_xlim(0, 100)
st.pyplot(fig)

# --- Chart: Total Questions Answered ---
st.subheader("📈 Total Questions Answered")
fig2, ax2 = plt.subplots()
ax2.bar(summary["topic"], summary["total"], color="lightgreen")
ax2.set_ylabel("Total Answered")
st.pyplot(fig2)

# --- Download CSV ---
st.download_button(
    label="📥 Download CSV Report",
    data=summary.to_csv(index=False).encode('utf-8'),
    file_name=f"encor_summary_{option.replace(' ', '_').lower()}.csv",
    mime="text/csv"
)