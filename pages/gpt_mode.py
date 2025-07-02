import streamlit as st
import openai
import time
import random
import os, sys

# Add root dir to path (fix import if needed)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quiz_logic import check_answer
from result_logger_supabase import log_result_supabase

st.set_page_config(page_title="🧠 GPT Quiz Mode", layout="centered")
st.title("🧠 GPT Mode – Real-time Question Generator")

openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_gpt_question():
    prompt = """
You are an expert CCNP ENCOR instructor. Generate one multiple-choice question (with 4 options A, B, C, D) based on the CCNP 350-401 ENCOR exam. Format it as a JSON object with the following keys: 'id', 'question', 'options', 'answer', and 'explanation'.

Ensure:
- 'id' is a unique timestamp-based ID
- 'question' is concise
- 'options' is a dictionary with keys A, B, C, D
- 'answer' is a list of correct option letters (can be more than one)
- 'explanation' is clear and short

Output only the JSON.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    import json
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)

# Init session state
if 'gpt_question' not in st.session_state:
    st.session_state.gpt_question = generate_gpt_question()
    st.session_state.submitted = False

q = st.session_state.gpt_question
st.subheader(f"🧩 {q['question']}")

opts = q['options']
option_labels = [f"{k}: {v}" for k, v in opts.items()]
selection = st.multiselect("Choose your answer:", option_labels, disabled=st.session_state.submitted)

label_map = {f"{k}: {v}": k for k, v in opts.items()}
user_answer = [label_map[s] for s in selection]

if not st.session_state.submitted:
    if st.button("✅ Submit Answer"):
        correct = check_answer(user_answer, q['answer'])
        st.session_state.submitted = True

        if correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")

        with st.expander("💡 Explanation"):
            st.write(q['explanation'])

        log_result_supabase(q['id'], "GPT", correct, 0)

if st.session_state.submitted:
    if st.button("🔄 Next Question"):
        st.session_state.gpt_question = generate_gpt_question()
        st.session_state.submitted = False
        st.rerun()