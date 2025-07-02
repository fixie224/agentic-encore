import streamlit as st
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase
from auth import is_user_approved
from admin import is_admin

# --- Login & approval check ---
email = st.session_state.get("user_email", None)

if not email:
    st.warning("⚠️ Anda perlu login untuk akses halaman ini.")
    st.page_link("pages/login.py", label="🔐 Pergi ke Login", icon="🔑")
    st.stop()

if not is_user_approved(email):
    st.error("❌ Akaun anda belum diluluskan. Sila tunggu pengesahan admin.")
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

# --- GPT Mode Only UI ---
st.set_page_config(page_title="GPT Mode Only", layout="centered")
st.title("🧠 GPT Mode Only — Real-time CCNP-style Generator")

# --- Select topic and difficulty ---
topic = st.selectbox("🗂️ Pilih Topik", ["OSPF", "BGP", "VXLAN", "SD-Access", "QoS", "Security"])
difficulty = st.selectbox("🎯 Tahap Kesukaran", ["easy", "medium", "hard"])

# --- Generate single question on load or regenerate ---
if "gpt_question" not in st.session_state or st.button("🔄 Jana Soalan Baru"):
    with st.spinner("Generating question..."):
        q = generate_encor_question_v1(topic=topic, difficulty=difficulty)
        st.session_state.gpt_question = q
        st.session_state.gpt_answered = False

# --- Show Question ---
if "gpt_question" in st.session_state:
    q = st.session_state.gpt_question

    st.markdown(f"### ❓ {q['question']}")
    selected = st.radio("Jawapan anda:", list(q["options"].keys()),
                        format_func=lambda x: f"{x}. {q['options'][x]}")

    if st.button("✅ Submit Jawapan") and not st.session_state.get("gpt_answered", False):
        is_correct = selected in q["answer"]
        if is_correct:
            st.success("✅ Betul!")
        else:
            st.error(f"❌ Salah. Jawapan betul: {', '.join(q['answer'])}")
        st.info(f"💡 Penjelasan: {q['explanation']}")
        st.session_state.gpt_answered = True

        # Log to Supabase
        log_result_supabase(
            question_id="gpt_mode_only",
            is_correct=is_correct,
            topic=q["topic"],
            source="gpt_mode_only"
        )