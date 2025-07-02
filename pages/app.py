import streamlit as st
import random
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase, init_db

st.set_page_config(page_title="Quiz Mode (Static)", page_icon="📝")
st.title("📝 Static Quiz Mode (350-401 ENCOR)")

if "static_questions" not in st.session_state:
    st.session_state.static_questions = []
    st.session_state.current_q_index = 0
    st.session_state.score = 0

# Load sample static questions
STATIC_QUESTIONS = [
    {
        "question": "Apakah fungsi protokol OSPF dalam rangkaian?",
        "options": {
            "A": "Menetapkan alamat IP",
            "B": "Menguruskan NAT",
            "C": "Menentukan laluan terbaik",
            "D": "Menukar MAC Address"
        },
        "answer": ["C"],
        "explanation": "OSPF digunakan untuk menentukan laluan terbaik dalam rangkaian IP.",
        "topic": "Routing"
    },
    {
        "question": "Apakah port default untuk HTTPS?",
        "options": {
            "A": "80",
            "B": "20",
            "C": "443",
            "D": "21"
        },
        "answer": ["C"],
        "explanation": "Port 443 digunakan untuk HTTPS.",
        "topic": "Security"
    }
]

if not st.session_state.static_questions:
    st.session_state.static_questions = random.sample(STATIC_QUESTIONS, len(STATIC_QUESTIONS))

current_q = st.session_state.static_questions[st.session_state.current_q_index]

st.markdown(f"### ❓ {current_q['question']}")
selected = st.radio("Pilihan anda:", list(current_q["options"].keys()),
                    format_func=lambda x: f"{x}: {current_q['options'][x]}")

if st.button("Submit"):
    correct = selected in current_q["answer"]
    if correct:
        st.success("✅ Betul!")
        st.session_state.score += 1
    else:
        st.error("❌ Salah")

    st.markdown(f"### Jawapan betul: {', '.join(current_q['answer'])}")
    st.info(f"💡 {current_q['explanation']}")

    # Log to Supabase
    log_result_supabase(
        question_id=f"static_{st.session_state.current_q_index}",
        is_correct=correct,
        topic=current_q["topic"],
        source="static"
    )

    if st.session_state.current_q_index + 1 < len(st.session_state.static_questions):
        if st.button("Soalan Seterusnya"):
            st.session_state.current_q_index += 1
            st.experimental_rerun()
    else:
        st.markdown(f"## 🏁 Tamat! Skor anda: {st.session_state.score}/{len(st.session_state.static_questions)}")
        if st.button("Mula Semula"):
            st.session_state.static_questions = []
            st.session_state.current_q_index = 0
            st.session_state.score = 0
            st.experimental_rerun()