import requests
from datetime import datetime
import os
import streamlit as st

# --- CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
TABLE_NAME = "results"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- LOG RESULT TO SUPABASE ---
def log_result_supabase(question_id, topic, is_correct, time_taken):
    payload = {
        "question_id": question_id,
        "topic": topic,
        "is_correct": is_correct,
        "time_taken": time_taken,
        "timestamp": datetime.now().isoformat()
    }
    res = requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}", json=payload, headers=HEADERS)
    if res.status_code not in (200, 201):
        print("Error logging result:", res.text)

# --- GET TOPIC SUMMARY ---
def get_topic_summary_supabase(raw=False):
    url = f"{SUPABASE_URL}/rest/v1/results?select=topic,is_correct,timestamp"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print("Error fetching summary:", res.text)
        return []

    data = res.json()
    if raw:
        return data

    summary = {}
    for row in data:
        topic = row['topic']
        if topic not in summary:
            summary[topic] = {"total": 0, "correct": 0}
        summary[topic]["total"] += 1
        if row["is_correct"]:
            summary[topic]["correct"] += 1

    return [(t, v["total"], v["correct"]) for t, v in summary.items()]

# --- OPTIONAL INIT ---
def init_db():
    pass