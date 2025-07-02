import streamlit as st

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

    if st.button("🧬 GPT Quiz Only"):
        st.switch_page("pages/gpt_mode_only.py")

with col2:
    if st.button("🔎 Review Incorrect Questions"):
        st.switch_page("pages/review_mode.py")

    if st.button("📊 Dashboard & Analytics"):
        st.switch_page("pages/dashboard.py")

    if st.button("🔬 Lab Simulation"):
        st.switch_page("pages/lab_sim.py")

    if st.button("⚡ Mixed Mode (80% static + 20% GPT)"):
        st.switch_page("pages/mixed_mode.py")

st.markdown("---")
st.markdown("🤖 Powered by 👨‍💻 Developed by Fizi")