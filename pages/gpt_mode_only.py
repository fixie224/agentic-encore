import streamlit as st
import openai
import random
import time
import sys, os

# --- SETUP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from quiz_logic import check_answer

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="🤖 GPT Mode Only", layout="centered")
st.title("🤖 CCNP Quiz (GPT Mode)")

if 'submitted_gpt' not in st.session_state:
    st.session_state.submitted_gpt = False

if 'current_q' not in st.session_state:
    st.session_state.current_q = {}

if 'score_gpt' not in st.session_state:
    st.session_state.score_gpt = 0

# --- GPT GENERATION ---
def generate_question():
    prompt = """
You are a Cisco-certified instructor. Generate a CCNP ENCOR-level multiple-choice question in the following JSON format:
{
  "id": "unique_id",
  "question": "...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "answer": ["A"],
  "explanation": "...",
  "topic": "Layer 3 Technologies"
}
Ensure technical accuracy and randomness. Use various topics across ENCOR.
"""
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    try:
        raw = res['choices'][0]['message']['content']
        q = eval(raw)
        return q
    except:
        return None

# --- FETCH QUESTION ---
if not st.session_state.current_q:
    with st.spinner("🔄 Generating question..."):
        st.session_state.current_q = generate_question()

q = st.session_state.current_q

if not q:
    st.error("❌ Failed to generate question. Try again.")
    st.stop()

qid = q['id']
opts = q['options']

st.markdown(f"### 📘 {q['topic']}")
st.markdown(f"#### {q['question']}")

option_keys = list(opts.keys())
random.shuffle(option_keys)
label_map = {f"{k}: {opts[k]}": k for k in option_keys}

selection = st.multiselect("Select your answer:", list(label_map.keys()), disabled=st.session_state.submitted_gpt)
user_answer = [label_map[s] for s in selection]

# --- SUBMIT ---
if not st.session_state.submitted_gpt:
    if st.button("✅ Submit"):
        correct = check_answer(user_answer, q['answer'])
        st.session_state.submitted_gpt = True
        if correct:
            st.success("✅ Correct!")
            st.session_state.score_gpt += 1
        else:
            st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")
        with st.expander("💡 Explanation"):
            st.write(q['explanation'])

# --- NEXT ---
if st.session_state.submitted_gpt:
    if st.button("➡️ Next Question"):
        st.session_state.current_q = {}
        st.session_state.submitted_gpt = False
        st.rerun()

# --- Score ---
st.markdown("---")
st.info(f"🧠 Score: {st.session_state.score_gpt}")