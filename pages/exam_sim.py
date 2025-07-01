import streamlit as st
import random
import time
from question_bank import load_questions
from quiz_logic import check_answer
from result_logger_supabase import log_result_supabase
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="📝 ENCOR Exam Simulator", layout="centered")
st.title("📝 CCNP 350-401 ENCOR – Full Exam Simulation")

# Load and shuffle questions
questions = load_questions()
random.shuffle(questions)
questions = questions[:50]

if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

# Timer setup
exam_duration = 7200  # 2 hours
elapsed_time = time.time() - st.session_state.start_time
time_left = exam_duration - elapsed_time
progress = min(elapsed_time / exam_duration, 1.0)

if time_left <= 0:
    st.warning("⏰ Time is up! Submitting all unanswered questions as blank.")
    for q in questions:
        qid = q['id']
        if qid not in st.session_state.answers:
            st.session_state.answers[qid] = []
    st.session_state.exam_finished = True

# Timer bar
st.progress(progress, text=f"⏳ Time Remaining: {int(time_left // 60):02d}:{int(time_left % 60):02d}")

# Show questions
score = 0
total_per_topic = {}
correct_per_topic = {}

with st.form("exam_form"):
    for idx, q in enumerate(questions):
        qid = q['id']
        topic = q['topic']
        opts = q['options']

        st.markdown(f"### Q{idx+1}. ({topic}) {q['question']}")
        label_map = {f"{k}: {opts[k]}": k for k in opts}

        selected = st.multiselect(
            f"Answer for Q{idx+1}",
            options=list(label_map.keys()),
            default=[f"{k}: {opts[k]}" for k in st.session_state.answers.get(qid, [])],
            key=qid
        )
        st.session_state.answers[qid] = [label_map[s] for s in selected]

    submitted = st.form_submit_button("📝 Submit All Answers")

if submitted or st.session_state.get("exam_finished"):
    st.session_state.exam_finished = True
    st.markdown("---")
    st.header("📊 Exam Results")

    for idx, q in enumerate(questions):
        qid = q['id']
        topic = q['topic']
        answer = st.session_state.answers.get(qid, [])
        correct = check_answer(answer, q['answer'])
        log_result_supabase(qid, topic, correct, elapsed_time)

        total_per_topic[topic] = total_per_topic.get(topic, 0) + 1
        if correct:
            correct_per_topic[topic] = correct_per_topic.get(topic, 0) + 1
            st.success(f"Q{idx+1}: ✅ Correct")
            score += 1
        else:
            st.error(f"Q{idx+1}: ❌ Incorrect — Answer: {', '.join(q['answer'])}")

    st.success(f"🎉 Final Score: {score} / {len(questions)}")

    st.markdown("### 📘 Score by Topic:")
    for topic in total_per_topic:
        total = total_per_topic[topic]
        correct = correct_per_topic.get(topic, 0)
        st.markdown(f"- **{topic}**: {correct} / {total} correct")