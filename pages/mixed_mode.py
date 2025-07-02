import streamlit as st
import random
from gpt_generator import generate_encor_question_v1
from result_logger_supabase import log_result_supabase
from auth import is_user_approved
from admin import is_admin

# --- Semak Login & Kelulusan ---
email = st.session_state.get("user_email", None)

if not email:
    st.warning("⚠️ Anda perlu login untuk akses halaman ini.")
    st.page_link("pages/login.py", label="🔐 Pergi ke Login", icon="🔑")
    st.stop()

if not is_user_approved(email):
    st.error("❌ Akaun anda belum diluluskan. Sila tunggu kelulusan admin.")
    st.stop()

if is_admin(email):
    st.success("✅ Anda log masuk sebagai admin.")

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"👋 Logged in as `{email}`")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Config ---
st.set_page_config(page_title="🧠 Mixed Mode", layout="centered")
st.title("🧠 Mixed Quiz Mode")

# --- Static question bank ---
static_questions = [
    {
        "question_id": "q1",
        "question": "Which protocol is used to encapsulate PPP frames in Ethernet frames?",
        "options": {"A": "PPP over Ethernet", "B": "L2TP", "C": "GRE", "D": "MPLS"},
        "answer": ["A"],
        "explanation": "PPP over Ethernet (PPPoE) is the correct encapsulation method.",
        "topic": "WAN"
    },
    {
        "question_id": "q2",
        "question": "What is the purpose of LSA type 1 in OSPF?",
        "options": {"A": "Summarize external routes", "B": "Advertise local router's interfaces", "C": "Advertise default route", "D": "Summarize inter-area routes"},
        "answer": ["B"],
        "explanation": "LSA type 1 advertises directly connected interfaces of the router.",
        "topic": "OSPF"
    },
]

# --- Init Session State ---
if "mixed_mode" not in st.session_state:
    st.session_state.mixed_mode = {
        "mode": random.choices(["static", "gpt"], weights=[0.7, 0.3])[0],
        "current_question": None,
        "answered": False
    }

mode = st.session_state.mixed_mode["mode"]

# --- Load Question ---
if not st.session_state.mixed_mode["current_question"]:
    if mode == "static":
        st.session_state.mixed_mode["current_question"] = random.choice(static_questions)
    else:
        st.session_state.mixed_mode["current_question"] = generate_encor_question_v1(topic="OSPF", difficulty="medium")

q = st.session_state.mixed_mode["current_question"]
st.write(f"#### Question ({mode.upper()}): {q['question']}")

# --- Display options ---
selected = st.radio(
    "Choose your answer:",
    list(q["options"].keys()),
    format_func=lambda x: f"{x}: {q['options'][x]}",
    index=0,
    disabled=st.session_state.mixed_mode["answered"]
)

# --- Submit Answer ---
if st.button("Submit Answer") and not st.session_state.mixed_mode["answered"]:
    is_correct = selected in q["answer"]
    st.session_state.mixed_mode["answered"] = True

    log_result_supabase(
        question_id=q.get("question_id", f"gpt_{random.randint(1000,9999)}"),
        is_correct=is_correct,
        topic=q.get("topic", "unknown"),
        source=mode
    )

    if is_correct:
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Incorrect. Correct: {', '.join(q['answer'])}")
    st.info(f"💡 Explanation: {q['explanation']}")

# --- Next Button ---
if st.session_state.mixed_mode["answered"]:
    if st.button("Next Question"):
        st.session_state.mixed_mode = {
            "mode": random.choices(["static", "gpt"], weights=[0.7, 0.3])[0],
            "current_question": None,
            "answered": False
        }
        st.experimental_rerun()