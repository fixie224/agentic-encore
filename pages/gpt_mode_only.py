import streamlit as st
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase

st.set_page_config(page_title="GPT Quiz Mode", layout="centered")

st.title("🧠 GPT Quiz Mode (CCNP Style)")

# --- Select topic and difficulty ---
topic = st.selectbox("Select Topic", ["OSPF", "BGP", "VXLAN", "SD-Access", "QoS", "Security"])
difficulty = st.selectbox("Select Difficulty", ["easy", "medium", "hard"])

# --- Generate question ---
if "gpt_questions" not in st.session_state:
    st.session_state.gpt_questions = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if st.button("🌀 Generate Question"):
    with st.spinner("Generating CCNP-style question..."):
        q = generate_encor_question_v1(topic, difficulty)
        if q:
            st.session_state.gpt_questions.append(q)
            st.session_state.current_q = len(st.session_state.gpt_questions) - 1

if st.session_state.gpt_questions:
    q = st.session_state.gpt_questions[st.session_state.current_q]
    st.markdown(f"**Question {st.session_state.current_q + 1}:** {q['question']}")
    selected = st.radio("Choose an answer:", list(q["options"].keys()), format_func=lambda x: f"{x}. {q['options'][x]}")

    if st.button("Submit Answer"):
        is_correct = selected in q["answer"]
        st.success("✅ Correct!") if is_correct else st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")
        st.info(f"🧠 Explanation: {q['explanation']}")

        # Log result
        log_result_supabase(
            question_id=f"gpt_{st.session_state.current_q}",
            is_correct=is_correct,
            topic=q["topic"],
            source="gpt"
        )