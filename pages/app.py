import streamlit as st
import random
import time
import sys, os

# Fix import path for /pages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from question_bank import load_questions
from quiz_logic import check_answer, get_explanation
from tracker import log_result
from result_logger_supabase import log_result_supabase, init_db
from gpt_generator import generate_ccnp_question
from gpt_generator import generate_gpt_question

init_db()

st.set_page_config(page_title='Agentic ENCOR Quiz', layout='centered')
st.title('🧠 Agentic AI – CCNP 350-401 ENCOR Quiz')

# Load questions and topics
static_questions = load_questions()
all_topics = sorted(set(q['topic'] for q in static_questions))

# --- Mode Selection ---
mode = st.radio("Select Quiz Mode:", ["Mixed Mode", "GPT Mode Only", "GPT + Supabase Log"])

# --- Topic Selection ---
selected_topic = st.selectbox("📂 Select Topic:", ["All"] + all_topics)

# --- Reset Quiz ---
if st.button("🔁 Reset Quiz"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Prepare Questions ---
if 'questions' not in st.session_state:
    if mode == "Mixed Mode":
        static_part = static_questions if selected_topic == "All" else [q for q in static_questions if q['topic'] == selected_topic]
        random.shuffle(static_part)
        static_part = static_part[:8]  # 80%
        gpt_part = [generate_ccnp_question(selected_topic if selected_topic != "All" else None) for _ in range(2)]
        st.session_state.questions = static_part + gpt_part
    elif mode == "GPT Mode Only" or mode == "GPT + Supabase Log":
        st.session_state.questions = [generate_ccnp_question(selected_topic if selected_topic != "All" else None) for _ in range(10)]
    random.shuffle(st.session_state.questions)

questions = st.session_state.questions

if 'submitted' not in st.session_state:
    st.session_state.submitted = {}

score = 0

for i, q in enumerate(questions):
    qid = q['id']
    topic = q['topic']
    st.markdown(f"### 📘 Topic: {topic}")
    st.subheader(q['question'])

    opts = q['options']
    option_keys = list(opts.keys())
    random.shuffle(option_keys)
    label_map = {f"{k}: {opts[k]}": k for k in option_keys}

    disabled = st.session_state.submitted.get(qid, False)

    user_selection = st.multiselect(
        f"Select answer(s) for Question {qid}",
        options=list(label_map.keys()),
        key=qid,
        disabled=disabled
    )
    user_answer = [label_map[sel] for sel in user_selection]

    if not disabled:
        if st.button(f"Submit Answer {qid}", key=f"btn_{qid}"):
            st.session_state.submitted[qid] = True

    if st.session_state.submitted.get(qid):
        correct = check_answer(user_answer, q['answer'])
        if correct:
            st.success('✅ Correct!')
            score += 1
        else:
            st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")

        st.info(f"⏱️ Time taken: {round(time.time() - st.session_state.get(f'start_{qid}', time.time()), 1)} sec")

        with st.expander("💡 Explanation"):
            st.write(get_explanation(q))

        # Supabase log
        if mode == "GPT + Supabase Log":
            log_result_supabase(qid, topic, correct, 0)
        else:
            log_result(qid, correct)

# --- Final Score ---
st.markdown(f"## 🏁 Final Score: **{score} / {len(questions)}**")