import streamlit as st
import random
import time
from question_bank import load_questions
from quiz_logic import check_answer, get_explanation
from tracker import log_result
from result_logger import init_db
init_db()

st.set_page_config(page_title='Agentic ENCOR Quiz', layout='centered')
st.title('🧠 Agentic AI – CCNP 350-401 ENCOR Quiz')

# Load questions and detect topics
all_questions = load_questions()
all_topics = sorted(set(q['topic'] for q in all_questions))

# Focus mode (based on weak topics)
focus_mode = st.checkbox("🎯 Focus on Weak Topics Only")

# Track selected topic
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = "All"

new_topic = st.selectbox("📂 Select Topic:", options=["All"] + all_topics)

if new_topic != st.session_state.selected_topic:
    st.session_state.selected_topic = new_topic
    if 'shuffled_questions' in st.session_state:
        del st.session_state['shuffled_questions']
    st.rerun()

selected_topic = st.session_state.selected_topic

# Reset Quiz
if st.button("🔁 Reset Quiz"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Select filtered questions
if focus_mode and 'weak_topics' in st.session_state:
    weak = st.session_state['weak_topics']
    weak_sorted = sorted(weak.items(), key=lambda x: x[1], reverse=True)
    weakest_topics = [t for t, count in weak_sorted[:2]]
    st.info(f"🧠 Focusing on weak topics: {', '.join(weakest_topics)}")
    filtered_questions = [q for q in all_questions if q['topic'] in weakest_topics]
else:
    filtered_questions = all_questions if selected_topic == "All" else [q for q in all_questions if q['topic'] == selected_topic]

# Shuffle once per session
if 'shuffled_questions' not in st.session_state:
    random.shuffle(filtered_questions)
    st.session_state.shuffled_questions = filtered_questions
else:
    filtered_questions = st.session_state.shuffled_questions

# Init state
if 'submitted' not in st.session_state:
    st.session_state.submitted = {}
if 'option_orders' not in st.session_state:
    st.session_state.option_orders = {}
if 'weak_topics' not in st.session_state:
    st.session_state.weak_topics = {}

score = 0
total_per_topic = {}
correct_per_topic = {}

# Quiz Loop
for q in filtered_questions:
    topic = q['topic']
    qid = q['id']
    st.markdown(f"### 📘 Topic: {topic}")
    st.subheader(q['question'])

    opts = q['options']

    # Shuffle answer options once
    if qid not in st.session_state.option_orders:
        option_keys = list(opts.keys())
        random.shuffle(option_keys)
        st.session_state.option_orders[qid] = option_keys
    else:
        option_keys = st.session_state.option_orders[qid]

    label_map = {f"{k}: {opts[k]}": k for k in option_keys}

    submitted_key = f"submitted_{qid}"
    if submitted_key not in st.session_state:
        st.session_state[submitted_key] = False

    disabled = st.session_state[submitted_key]

    # Timer start
    timer_key = f"start_time_{qid}"
    if timer_key not in st.session_state:
        st.session_state[timer_key] = time.time()

    user_selection = st.multiselect(
        f"Select answer(s) for Question {qid}",
        options=list(label_map.keys()),
        key=qid,
        disabled=disabled
    )
    user_answer = [label_map[sel] for sel in user_selection]

    if not st.session_state[submitted_key]:
        if st.button(f"Submit Answer {qid}", key=f"btn_{qid}"):
            st.session_state.submitted[qid] = user_answer
            st.session_state[submitted_key] = True

    if st.session_state[submitted_key]:
        user_answer = st.session_state.submitted[qid]
        correct = check_answer(user_answer, q['answer'])
        if correct:
            st.success('✅ Correct!')
            score += 1
        else:
            st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")

        elapsed = time.time() - st.session_state[timer_key]
        st.info(f"⏱️ Time taken: {elapsed:.1f} seconds")

        with st.expander("💡 Explanation"):
            st.write(get_explanation(q))
            log_result(qid, correct)

        # Score tracking
        total_per_topic[topic] = total_per_topic.get(topic, 0) + 1
        if correct:
            correct_per_topic[topic] = correct_per_topic.get(topic, 0) + 1
        else:
            st.session_state.weak_topics[topic] = st.session_state.weak_topics.get(topic, 0) + 1

# Final Score
st.markdown(f"## 🏁 Final Score: **{score} / {len(filtered_questions)}**")

if total_per_topic:
    st.markdown("### 📊 Score by Topic:")
    for topic in total_per_topic:
        c = correct_per_topic.get(topic, 0)
        t = total_per_topic[topic]
        st.markdown(f"- **{topic}**: {c} / {t} correct")