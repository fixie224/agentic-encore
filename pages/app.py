import streamlit as st
import random
import time
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from question_bank import load_questions
from quiz_logic import check_answer, get_explanation
from result_logger_supabase import log_result_supabase, init_db

init_db()

st.set_page_config(page_title='📝 Quiz Mode', layout='centered')
st.title('🧠 Agentic AI – CCNP 350-401 Quiz')

all_questions = load_questions()
all_topics = sorted(set(q['topic'] for q in all_questions))

# Topic filter
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = "All"

selected = st.selectbox("📂 Filter by Topic:", ["All"] + all_topics)
if selected != st.session_state.selected_topic:
    st.session_state.selected_topic = selected
    st.rerun()

filtered_questions = [q for q in all_questions if selected == "All" or q['topic'] == selected]
random.shuffle(filtered_questions)

if 'submitted' not in st.session_state:
    st.session_state.submitted = {}
if 'option_orders' not in st.session_state:
    st.session_state.option_orders = {}

score = 0

for q in filtered_questions:
    qid = q['id']
    topic = q['topic']
    st.markdown(f"### 📘 {topic}: {q['question']}")

    opts = q['options']
    if qid not in st.session_state.option_orders:
        keys = list(opts.keys())
        random.shuffle(keys)
        st.session_state.option_orders[qid] = keys
    else:
        keys = st.session_state.option_orders[qid]

    label_map = {f"{k}: {opts[k]}": k for k in keys}
    disabled = st.session_state.submitted.get(qid, False)

    selection = st.multiselect(
        f"Select your answer (QID {qid})",
        list(label_map.keys()),
        key=f"ans_{qid}",
        disabled=disabled
    )

    answer = [label_map[s] for s in selection]

    if not disabled:
        if st.button(f"Submit {qid}", key=f"btn_{qid}"):
            st.session_state.submitted[qid] = True
            correct = check_answer(answer, q['answer'])
            if correct:
                st.success("✅ Correct!")
                score += 1
            else:
                st.error(f"❌ Incorrect. Answer: {', '.join(q['answer'])}")
            with st.expander("💡 Explanation"):
                st.write(get_explanation(q))
            log_result_supabase(qid, topic, correct, time.time())

st.markdown("---")
st.markdown(f"### ✅ Final Score: {score} / {len(filtered_questions)}")