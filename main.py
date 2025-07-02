import streamlit as st

if "user_email" not in st.session_state:
    st.warning("⚠️ Anda perlu login untuk akses sistem.")
    st.page_link("pages/login.py", label="🔐 Pergi ke Login", icon="🔑")
    st.stop()

st.set_page_config(page_title="Agentic ENCOR Hub", layout="centered")
st.title("Bantuan Belajar – CCNP 350-401 Hub")

st.markdown("---")
st.markdown("### 🚀 Choose a Mode:")

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 Quiz Mode (Static)"):
        st.switch_page("pages/app.py")

    if st.button("🧪 Exam Simulation"):
        st.switch_page("pages/exam_sim.py")

    if st.button("🧠 Flashcard Mode"):
        st.switch_page("pages/flashcard_mode.py")

with col2:
    if st.button("🔎 Review Incorrect Questions"):
        st.switch_page("pages/review_mode.py")

    if st.button("📊 Dashboard & Analytics"):
        st.switch_page("pages/dashboard.py")

    if st.button("🔬 Lab Simulation"):
        st.switch_page("pages/lab_sim.py")

st.markdown("---")
st.markdown("### 🤖 GPT-Integrated Modes")

col3, col4 = st.columns(2)

with col3:
    if st.button("⚡ Mixed Mode (80% Static + 20% GPT)"):
        st.switch_page("pages/mixed_mode.py")

    if st.button("🤖 GPT Mode Only"):
        st.switch_page("pages/gpt_mode_only.py")

with col4:
    if st.button("📦 GPT + Supabase Log"):
        st.switch_page("pages/gpt_quiz_mode.py")

st.markdown("---")
st.markdown("👨‍💻 Built by Fizi ")