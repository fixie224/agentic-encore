import streamlit as st
import random
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase

st.set_page_config(page_title="🧠 Mixed Mode", layout="centered")
st.title("🧠 Mixed Quiz Mode")

# Load static questions (replace with your real static question bank)
static_questions = [
    {
        "question_id": "q1",
        "question": "Which protocol is used to encapsulate PPP frames in Ethernet frames?",
        "options": {"A": "PPP over Ethernet", "B": "L2TP", "C": "GRE", "D": "MPLS"},
        "answer": ["A"],
        "explanation": "PPP over Ethernet (PPPoE) is the correct encapsulation method."
    },
    {
        "question_id": "q2",
        "question": "What is the purpose of LSA type 1 in OSPF?",
        "options": {"A": "Summarize external routes", "B": "Advertise local router's interfaces", "C": "Advertise default route", "D": "Summarize inter-area routes"},
        "answer": ["B"],
        "explanation": "LSA type 1 advertises directly connected interfaces of the router."
    },
]

# --- Session Init ---
if "mode" not in st.session_state:
    st.session_state.mode = random.choices(["static", "gpt"], weights=[0.8, 0.2])[0]
    st.session_state.current_question = None
    st.session_state.answered = False

# --- Load Question ---
if not st.session_state.current_question:
    if st.session_state.mode == "static":
        st.session_state.current_question = random.choice(static_questions)
    else:
        st.session_state.current_question = generate_encor_question_v1("OSPF")  # Replace with topic selector

q = st.session_state.current_question
st.write("#### Question:", q["question"])

# --- Display Options ---
selected = st.radio("Choose one:", list(q["options"].keys()), format_func=lambda x: f"{x}: {q['options'][x]}", index=0, disabled=st.session_state.answered)

# --- Submit ---
if st.button("Submit Answer") and not st.session_state.answered:
    is_correct = selected in q["answer"]
    st.session_state.answered = True
    log_result_supabase(
        question_id=q.get("question_id", "gpt-q"),
        is_correct=is_correct,
        topic=q.get("topic", "OSPF"),
        source=st.session_state.mode
    )

    if is_correct:
        st.success("✅ Correct!")
    else:
        st.error("❌ Incorrect.")
    st.markdown(f"**Explanation:** {q['explanation']}")

# --- Next Button ---
if st.session_state.answered:
    if st.button("Next Question"):
        st.session_state.mode = random.choices(["static", "gpt"], weights=[0.8, 0.2])[0]
        st.session_state.current_question = None
        st.session_state.answered = False