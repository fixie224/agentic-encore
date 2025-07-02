# result_logger_supabase.py
from supabase import create_client
import streamlit as st
import datetime

# --- Setup Supabase Client ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Save a result to Supabase ---
def log_result_supabase(question_id, is_correct, topic, source="static"):
    if "user_email" not in st.session_state:
        return

    result = {
        "user_email": st.session_state["user_email"],
        "question_id": question_id,
        "is_correct": is_correct,
        "topic": topic,
        "source": source,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    try:
        supabase.table("results").insert(result).execute()
    except Exception as e:
        st.error(f"❌ Error logging result: {e}")

# --- Get topic-level summary (raw or aggregated) ---
def get_topic_summary_supabase(raw=False):
    if "user_email" not in st.session_state:
        return []

    try:
        response = (
            supabase.table("results")
            .select("*")
            .eq("user_email", st.session_state["user_email"])
            .execute()
        )
        data = response.data
        return data if raw else _aggregate_topic_summary(data)
    except Exception as e:
        st.error(f"❌ Failed to get summary: {e}")
        return []

# --- Helper: aggregate summary by topic ---
def _aggregate_topic_summary(data):
    from collections import defaultdict
    summary = defaultdict(lambda: {"total": 0, "correct": 0})

    for row in data:
        topic = row.get("topic", "Unknown")
        summary[topic]["total"] += 1
        if row.get("is_correct"):
            summary[topic]["correct"] += 1

    result = []
    for topic, counts in summary.items():
        result.append({
            "topic": topic,
            "total": counts["total"],
            "correct": counts["correct"],
            "Accuracy (%)": round((counts["correct"] / counts["total"]) * 100, 1)
        })
    return result

# --- Get all results (for review mode) ---
def get_all_results_supabase():
    if "user_email" not in st.session_state:
        return []
    try:
        response = (
            supabase.table("results")
            .select("*")
            .eq("user_email", st.session_state["user_email"])
            .execute()
        )
        return response.data
    except Exception as e:
        st.error(f"❌ Failed to get all results: {e}")
        return []

# --- (Optional) Filter by time range ---
def get_results_filtered_by_days(days=30):
    all_results = get_all_results_supabase()
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    return [r for r in all_results if datetime.datetime.fromisoformat(r["timestamp"]) >= cutoff]