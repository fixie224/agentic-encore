import openai
import requests
import uuid
import datetime
import os
import streamlit as st

# --- CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SUPABASE_TABLE = "gpt_questions"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- GENERATE CCNP QUESTION FROM GPT ---
def generate_gpt_question(topic="Mixed"):
    prompt = f"""
    Generate a CCNP 350-401 ENCOR multiple-choice question in JSON format.
    - Include: id (uuid), topic, question, options (A-D), answer (list), explanation.
    - Format strictly as JSON.
    - Topic: {topic if topic != 'Mixed' else 'random'}.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a certified Cisco instructor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    content = response['choices'][0]['message']['content']
    try:
        data = eval(content) if isinstance(content, str) else content
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        return data
    except Exception as e:
        print("❌ Error parsing GPT output:", e)
        return None

# --- STORE TO SUPABASE ---
def log_gpt_question(data):
    data['timestamp'] = datetime.datetime.now().isoformat()
    res = requests.post(f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}", json=data, headers=HEADERS)
    if res.status_code not in (200, 201):
        print("❌ Supabase log error:", res.text)