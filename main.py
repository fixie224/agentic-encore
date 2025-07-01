import streamlit as st

st.set_page_config(page_title="Agentic ENCOR Hub", layout="centered")
st.title("🧠 Agentic AI – CCNP 350-401 Hub")

st.markdown("---")
st.markdown("### 🚀 Choose a Mode:")

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 Quiz Mode"):
        st.switch_page("app.py")

    if st.button("🧪 Exam Simulation"):
        st.switch_page("exam_sim.py")

with col2:
    if st.button("🔎 Review Incorrect Questions"):
        st.switch_page("review_mode.py")

    if st.button("📊 Dashboard & Analytics"):
        st.switch_page("dashboard.py")

st.markdown("---")
st.markdown("👨‍💻 Developed with ❤️ using Streamlit + Supabase")