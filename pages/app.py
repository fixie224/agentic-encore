import streamlit as st
import random
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase
from auth import get_current_user

st.set_page_config(page_title="📝 Static Quiz Mode", page_icon="📝")
st.title("📝 Static Quiz Mode (350-401 ENCOR)")

# --- Authentication Check ---
user = get_current_user()
if not user:
    st.warning("🔐 Sila log masuk untuk akses kuiz.")
    st.stop()

if not user.get("is_approved", False):
    st.warning("⏳ Akaun anda belum diluluskan oleh admin.")
    st.stop()

# Simpan email user
st.session_state["user_email"] = user["email"]

# --- Static Question Bank ---
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

# --- Session State Initialization ---
if "static_questions" not in st.session_state:
    st.session_state.static_questions = random.sample(STATIC_QUESTIONS, len(STATIC_QUESTIONS))
    st.session_state.current_q_index = 0
    st.session_state.score = 0

current_q = st.session_state.static_questions[st.session_state.current_q_index]

# --- Display Question ---
st.markdown(f"### ❓ {current_q['question']}")
selected = st.radio(
    "Pilihan anda:",
    list(current_q["options"].keys()),
    format_func=lambda k: f"{k}: {current_q['options'][k]}"
)

# --- Submit Answer ---
if st.button("Submit"):
    correct = selected in current_q["answer"]
    if correct:
        st.success("✅ Betul!")
        st.session_state.score += 1
    else:
        st.error("❌ Salah")

    st.markdown(f"**✅ Jawapan betul:** {', '.join(current_q['answer'])}")
    st.info(f"💡 {current_q['explanation']}")

    # Log to Supabase
    log_result_supabase(
        question_id=f"static_{st.session_state.current_q_index}",
        is_correct=correct,
        topic=current_q["topic"],
        source="static"
    )

    # --- Next Logic ---
    if st.session_state.current_q_index + 1 < len(st.session_state.static_questions):
        if st.button("➡️ Soalan Seterusnya"):
            st.session_state.current_q_index += 1
            st.experimental_rerun()
    else:
        st.balloons()
        st.markdown(f"## 🏁 Tamat! Skor akhir anda: **{st.session_state.score} / {len(st.session_state.static_questions)}**")
        if st.button("🔁 Mula Semula"):
            del st.session_state["static_questions"]
            st.session_state.current_q_index = 0
            st.session_state.score = 0
            st.experimental_rerun()