import streamlit as st
import random
import time
import sys, os

# --- Import login & auth ---
from auth import require_login_and_approval
from admin import is_admin
from question_bank import load_questions
from quiz_logic import check_answer, get_explanation
from result_logger_supabase import log_result_supabase

# --- Config ---
st.set_page_config(page_title='🧪 Exam Simulation', layout='centered')
st.title("🧪 CCNP ENCOR Exam Simulation")

# --- Login & approval check (Stop here if fail) ---
email = require_login_and_approval()

# --- Optional admin display ---
if is_admin(email):
    st.success("✅ Anda ialah admin.")

# --- Sidebar info ---
with st.sidebar:
    st.markdown(f"👋 Logged in as: `{email}`")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Fix import path if run from /pages ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Load + shuffle questions ---
questions = load_questions()
random.shuffle(questions)

# --- Start timer ---
if 'exam_start_time' not in st.session_state:
    st.session_state.exam_start_time = time.time()

# --- Init answers ---
if 'exam_answers' not in st.session_state:
    st.session_state.exam_answers = {}

score = 0

# --- Selection handler ---
def handle_selection(qid, selection, label_map):
    st.session_state.exam_answers[qid] = [label_map[s] for s in selection if s in label_map]

# --- Display questions ---
for q in questions:
    qid = q['id']
    topic = q['topic']
    st.markdown(f"#### 📘 {topic}: {q['question']}")

    opts = q['options']
    keys = list(opts.keys())
    random.shuffle(keys)
    label_map = {f"{k}: {opts[k]}" for k in keys}
    reverse_map = {f"{k}: {opts[k]}" for k in keys}

    key_name = f"exam_{qid}"
    default_labels = [f"{k}: {opts[k]}" for k in st.session_state.exam_answers.get(qid, []) if k in opts]

    selection = st.multiselect(
        f"Choose your answer (QID: {qid})",
        options=list(label_map.keys()),
        default=default_labels,
        key=key_name,
        on_change=lambda qid=qid, label_map=label_map: handle_selection(
            qid, st.session_state.get(f"exam_{qid}", []), label_map
        )
    )

    # Always update session
    handle_selection(qid, selection, label_map)

# --- Submit Exam ---
if st.button("✅ Submit Exam"):
    end_time = time.time()
    elapsed = end_time - st.session_state.exam_start_time
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

        log_result_supabase(question_id=qid, topic=q['topic'], is_correct=correct, source="exam_sim")

        with st.expander("💡 Explanation"):
            st.write(get_explanation(q))

    st.markdown("---")
    st.markdown(f"## 🎯 Final Score: **{score} / {len(questions)}**")