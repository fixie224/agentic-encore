import streamlit as st
import openai
import random
import time
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from quiz_logic import check_answer
from result_logger_supabase import log_result_supabase

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="🤖 GPT Quiz Mode", layout="centered")
st.title("🤖 GPT-Generated CCNP ENCOR Quiz")

if "gpt_questions" not in st.session_state:
    st.session_state.gpt_questions = []
    st.session_state.current_q = 0
    st.session_state.submitted = {}
    st.session_state.start_times = {}
    st.session_state.shuffled_opts = {}

# --- GPT Question Generator ---
def generate_gpt_question():
    prompt = (
        "You are a CCNP 350-401 ENCOR instructor. Generate ONE multiple-choice question. "
        "Use this format in JSON: {\n"
        "  'question': '...',\n"
        "  'options': {'A': '...', 'B': '...', 'C': '...', 'D': '...'},\n"
        "  'answer': ['A', 'C'],  # one or more\n"
        "  'explanation': '...'\n"
        "}. Only return the JSON object."
    )
    
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        text = res.choices[0].message.content.strip()
        json_data = eval(text) if text.startswith("{") else {}
        if all(k in json_data for k in ["question", "options", "answer", "explanation"]):
            return json_data
    except Exception as e:
        st.error(f"Error generating question: {e}")
    return None

# --- Generate if needed ---
if len(st.session_state.gpt_questions) <= st.session_state.current_q:
    new_q = generate_gpt_question()
    if new_q:
        new_q["id"] = len(st.session_state.gpt_questions) + 1
        st.session_state.gpt_questions.append(new_q)

# --- Show Question ---
q = st.session_state.gpt_questions[st.session_state.current_q]
qid = q["id"]
opts = q["options"]

st.markdown(f"### Q{qid}: {q['question']}")

# Shuffle options once
if qid not in st.session_state.shuffled_opts:
    st.session_state.shuffled_opts[qid] = random.sample(list(opts.keys()), len(opts))
option_keys = st.session_state.shuffled_opts[qid]
label_map = {f"{k}: {opts[k]}": k for k in option_keys}

# Timer
if qid not in st.session_state.start_times:
    st.session_state.start_times[qid] = time.time()

submitted = st.session_state.submitted.get(qid, False)
selection = st.multiselect("Select answer(s):", list(label_map.keys()), disabled=submitted)
user_answer = [label_map[s] for s in selection]

# Submit button
if not submitted and st.button("✅ Submit"):
    st.session_state.submitted[qid] = True
    correct = check_answer(user_answer, q["answer"])
    elapsed = time.time() - st.session_state.start_times[qid]
    
    if correct:
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")

    with st.expander("💡 Explanation"):
        st.write(q["explanation"])

    # Log
    log_result_supabase(qid, "GPT", correct, elapsed)

# Next Question
if submitted:
    if st.button("➡️ Next Question"):
        st.session_state.current_q += 1
        st.rerun()