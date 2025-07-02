import streamlit as st
import random
import time
import sys, os

# Fix import path if run from /pages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from question_bank import load_questions
from quiz_logic import check_answer, get_explanation
from result_logger_supabase import log_result_supabase
from gpt_generator import generate_gpt_question

st.set_page_config(page_title='🧪 Exam Simulation', layout='centered')
st.title("🧪 CCNP ENCOR Exam Simulation")

# --- Load questions and randomize ---
questions = load_questions()
random.shuffle(questions)

# --- Timer start ---
start_time = time.time()
st.info("⏱️ Timer started. Try to complete all questions!")

# --- Session state ---
if 'exam_answers' not in st.session_state:
    st.session_state.exam_answers = {}

score = 0

# --- Loop through questions ---
for q in questions:
    qid = q['id']
    topic = q['topic']
    st.markdown(f"#### 📘 {topic}: {q['question']}")

    opts = q['options']
    keys = list(opts.keys())
    random.shuffle(keys)
    label_map = {f"{k}: {opts[k]}": k for k in keys}

    selection = st.multiselect(
        f"Choose your answer (QID: {qid})",
        list(label_map.keys()),
        key=f"exam_{qid}"
    )

    user_ans = [label_map[s] for s in selection]
    st.session_state.exam_answers[qid] = user_ans

# --- Submit Exam ---
if st.button("✅ Submit Exam"):
    end_time = time.time()
    elapsed = end_time - start_time
    st.success(f"⏱️ Exam completed in {elapsed/60:.2f} minutes")

    for q in questions:
        qid = q['id']
        user_ans = st.session_state.exam_answers.get(qid, [])
        correct = check_answer(user_ans, q['answer'])
        if correct:
            st.success(f"✅ Q{qid}: Correct")
            score += 1
        else:
            st.error(f"❌ Q{qid}: Incorrect — Correct: {', '.join(q['answer'])}")

        # Log result
        log_result_supabase(qid, q['topic'], correct, elapsed)

        with st.expander("💡 Explanation"):
            st.write(get_explanation(q))

    st.markdown("---")
    st.markdown(f"## 🎯 Final Score: **{score} / {len(questions)}**")