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
st.set_page_config(page_title="🤖 GPT Real-time Mode", layout="centered")
st.title("🤖 GPT Real-time Mode")

# --- Select topic and difficulty ---
topic = st.selectbox("📘 Pilih Topik", ["OSPF", "BGP", "VXLAN", "SD-Access", "QoS", "Security", "Switching"])
difficulty = st.selectbox("🎯 Tahap Kesukaran", ["easy", "medium", "hard"])

# --- Generate Question ---
if "gpt_question" not in st.session_state:
    st.session_state.gpt_question = generate_encor_question_v1(topic=topic, difficulty=difficulty)
    st.session_state.gpt_answered = False

if st.button("🔁 Generate New Question"):
    st.session_state.gpt_question = generate_encor_question_v1(topic=topic, difficulty=difficulty)
    st.session_state.gpt_answered = False

q = st.session_state.gpt_question

# --- Display Question ---
if q:
    st.markdown(f"### ❓ {q['question']}")
    selected = st.radio("Jawapan anda:", list(q["options"].keys()), format_func=lambda x: f"{x}. {q['options'][x]}")

    if st.button("✅ Submit Jawapan") and not st.session_state.get("gpt_answered", False):
        is_correct = selected in q["answer"]
        if is_correct:
            st.success("✅ Betul!")
        else:
            st.error(f"❌ Salah. Jawapan betul: {', '.join(q['answer'])}")
        st.info(f"💡 Penjelasan: {q['explanation']}")
        st.session_state.gpt_answered = True

        # Log result
        log_result_supabase(
            question_id="gpt_mode_rt",
            is_correct=is_correct,
            topic=q.get("topic", topic),
            source="gpt_mode"
        )