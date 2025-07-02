import streamlit as st
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase

st.set_page_config(page_title="🧠 GPT Quiz Mode", layout="centered")
st.title("🧠 GPT Quiz Mode")

if "gpt_questions" not in st.session_state:
    st.session_state.gpt_questions = []
    st.session_state.current_q = 0

# Generate a new question if needed
if st.button("Generate New Question") or not st.session_state.gpt_questions:
    question = generate_encor_question_v1(topic="routing", difficulty="medium")
    if question:
        st.session_state.gpt_questions.append(question)
        st.session_state.current_q = len(st.session_state.gpt_questions) - 1

# Display the current question
if st.session_state.gpt_questions:
    q = st.session_state.gpt_questions[st.session_state.current_q]

    st.markdown(f"**Question:** {q['question']}")
    selected = st.radio("Choose your answer:", list(q["options"].items()), format_func=lambda x: f"{x[0]}. {x[1]}")

    if st.button("Submit Answer"):
        selected_key = selected[0]
        is_correct = selected_key in q["answer"]
        log_result_supabase(
            question_id=q.get("question_id", f"gpt_{st.session_state.current_q}"),
            is_correct=is_correct,
            topic=q.get("topic", "unknown"),
            source="gpt_quiz_mode"
        )
        if is_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect! Correct answer: {', '.join(q['answer'])}")
            st.info(q["explanation"])