import streamlit as st
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase
from auth import is_user_approved
from admin import is_admin

# --- Check login ---
email = st.session_state.get("user_email", None)

if not email:
    st.warning("⚠️ Anda perlu login untuk akses halaman ini.")
    st.page_link("pages/login.py", label="🔐 Pergi ke Login", icon="🔑")
    st.stop()

if not is_user_approved(email):
    st.error("❌ Akaun anda belum diluluskan. Sila tunggu kelulusan admin.")
    st.stop()

# --- Admin info ---
if is_admin(email):
    st.info("👑 Anda log masuk sebagai admin.")

# --- Sidebar logout ---
with st.sidebar:
    st.markdown(f"👋 Logged in as `{email}`")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- UI Config ---
st.set_page_config(page_title="🧠 GPT Quiz Mode", layout="centered")
st.title("🧠 GPT Quiz Mode")

# --- State Initialization ---
if "gpt_questions" not in st.session_state:
    st.session_state.gpt_questions = []
    st.session_state.current_q = 0

# --- Generate Question ---
if st.button("🔁 Generate New Question") or not st.session_state.gpt_questions:
    with st.spinner("🚀 Generating CCNP-style question..."):
        q = generate_encor_question_v1(topic="routing", difficulty="medium")
        if q:
            st.session_state.gpt_questions.append(q)
            st.session_state.current_q = len(st.session_state.gpt_questions) - 1

# --- Display Question ---
if st.session_state.gpt_questions:
    q = st.session_state.gpt_questions[st.session_state.current_q]

    st.markdown(f"### ❓ {q['question']}")
    selected = st.radio("Jawapan anda:", list(q["options"].keys()), format_func=lambda x: f"{x}. {q['options'][x]}")

    if st.button("✅ Submit Jawapan"):
        is_correct = selected in q["answer"]
        log_result_supabase(
            question_id=q.get("question_id", f"gpt_{st.session_state.current_q}"),
            is_correct=is_correct,
            topic=q.get("topic", "unknown"),
            source="gpt_quiz_mode"
        )
        if is_correct:
            st.success("✅ Betul!")
        else:
            st.error(f"❌ Salah. Jawapan betul: {', '.join(q['answer'])}")
            st.info(f"💡 {q['explanation']}")