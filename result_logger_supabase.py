# ==========================================
# 📄 result_logger_supabase.py
# ==========================================
import streamlit as st
from supabase import create_client
from datetime import datetime

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    try:
        supabase.table("results").select("*").limit(1).execute()
        return True
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        return False

def log_result_supabase(question_id: str, is_correct: bool, topic: str, source: str = "unknown"):
    try:
        supabase.table("results").insert({
            "question_id": question_id,
            "is_correct": is_correct,
            "topic": topic,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }).execute()
    except Exception as e:
        st.error(f"Error logging to Supabase: {e}")

def get_all_results_supabase():
    try:
        result = supabase.table("results").select("*").execute()
        return result.data if result and hasattr(result, "data") else []
    except Exception as e:
        st.error(f"Error fetching results: {e}")
        return []

def get_topic_summary_supabase(raw=False):
    data = get_all_results_supabase()
    if raw:
        return data
    summary = {}
    for row in data:
        topic = row.get("topic", "Unknown")
        if topic not in summary:
            summary[topic] = {"total": 0, "correct": 0}
        summary[topic]["total"] += 1
        if row.get("is_correct"):
            summary[topic]["correct"] += 1
    return summary