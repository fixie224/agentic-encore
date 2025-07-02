import streamlit as st
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase

st.set_page_config(page_title="🤖 GPT Real-time Mode", layout="centered")
st.title("🤖 GPT Real-time Mode")

if "gpt_question" not in st.session_state:
    st.session_state.gpt_question = generate_encor_question_v1(topic="switching", difficulty="medium")

if st.button("🔁 Generate New Question"):
    st.session_state.gpt_question = generate_encor_question_v1(topic="switching", difficulty="medium")

q = st.session_state.gpt_question

if q:
    st.markdown(f"**Question:** {q['question']}")
    selected = st.radio("Your answer:", list(q["options"].items()), format_func=lambda x: f"{x[0]}. {x[1]}")

    if st.button("Submit Answer"):
        selected_key = selected[0]
        is_correct = selected_key in q["answer"]
        log_result_supabase(
            question_id=q.get("question_id", "gpt_rt_1"),
            is_correct=is_correct,
            topic=q.get("topic", "unknown"),
            source="gpt_mode"
        )

        if is_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect! Correct answer: {', '.join(q['answer'])}")
            st.info(q["explanation"])