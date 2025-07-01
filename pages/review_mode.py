import streamlit as st
import random
import sys, os

# Fix path to import shared modules from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from question_bank import load_questions
from quiz_logic import check_answer, get_explanation
from result_logger_supabase import get_topic_summary_supabase

st.set_page_config(page_title='🔁 Review Mode', layout='centered')
st.title("🔁 Review Incorrect Questions")

# --- Load all questions ---
all_questions = load_questions()

# --- Load incorrect answers from Supabase ---
raw_data = get_topic_summary_supabase(raw=True)
wrong_by_topic = {}
for row in raw_data:
    if not row['is_correct']:
        topic = row['topic']
        wrong_by_topic[topic] = wrong_by_topic.get(topic, 0) + 1

if not wrong_by_topic:
    st.success("🎉 No incorrect answers logged. You're doing great!")
    st.stop()

# --- Select topic to review ---
sorted_weak = sorted(wrong_by_topic.items(), key=lambda x: x[1], reverse=True)
weak_topics = [t for t, _ in sorted_weak]
selected_topic = st.selectbox("📂 Select a weak topic to review:", weak_topics)

# --- Filter only incorrect questions from that topic ---
wrong_ids = [
    row['question_id']
    for row in raw_data
    if not row['is_correct'] and row['topic'] == selected_topic
]
questions = [q for q in all_questions if q['id'] in wrong_ids and q['topic'] == selected_topic]

if not questions:
    st.info("✅ No questions to retry for this topic.")
    st.stop()

random.shuffle(questions)

# --- Init session state ---
if 'review_submitted' not in st.session_state:
    st.session_state.review_submitted = {}

score = 0

# --- Question Loop ---
for q in questions:
    qid = q['id']
    st.markdown(f"### 🔁 Review: {q['question']}")

    opts = q['options']
    option_keys = list(opts.keys())
    random.shuffle(option_keys)
    label_map = {f"{k}: {opts[k]}": k for k in option_keys}

    disabled = st.session_state.review_submitted.get(qid, False)

    selection = st.multiselect(
        f"Choose your answer (QID: {qid})",
        list(label_map.keys()),
        key=f"review_{qid}",
        disabled=disabled
    )

    user_answer = [label_map[s] for s in selection]

    if not disabled:
        if st.button(f"Submit Answer {qid}", key=f"submit_{qid}"):
            st.session_state.review_submitted[qid] = True
            correct = check_answer(user_answer, q['answer'])
            if correct:
                st.success("✅ Correct!")
                score += 1
            else:
                st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")
            with st.expander("💡 Explanation"):
                st.write(get_explanation(q))

# --- Final Review Score ---
st.markdown("---")
st.success(f"🧠 Review Score for {selected_topic}: {score} / {len(questions)}")