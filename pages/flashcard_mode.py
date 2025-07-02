import streamlit as st
import sys, os
import random

from auth import require_login_and_approval
from admin import is_admin
from question_bank import load_questions

# --- Config ---
st.set_page_config(page_title="🧠 Flashcard Mode", layout="centered")
st.title("🧠 Flashcard Study Mode")

# --- Auth check ---
email = require_login_and_approval()

# --- Optional admin display ---
if is_admin(email):
    st.success("✅ Anda ialah admin.")

# --- Sidebar: user status & logout ---
with st.sidebar:
    st.markdown(f"👋 Logged in as: `{email}`")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Fix import path if run from /pages ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Load and filter flashcards ---
all_questions = load_questions()
all_topics = sorted(set(q['topic'] for q in all_questions))

selected_topic = st.selectbox("📂 Choose Topic:", ["All"] + all_topics)

if selected_topic == "All":
    flashcards = all_questions
else:
    flashcards = [q for q in all_questions if q['topic'] == selected_topic]

if not flashcards:
    st.info("No flashcards available for selected topic.")
    st.stop()

# --- Track flashcard index ---
if "flash_index" not in st.session_state:
    st.session_state.flash_index = 0

q = flashcards[st.session_state.flash_index]

# --- Show question ---
st.markdown(f"### 🔖 {q['question']}")

# --- Reveal answer ---
if st.button("🔄 Reveal Answer"):
    st.info("**Answer:** " + ", ".join(q['answer']))
    st.markdown("**Explanation:**")
    st.write(q.get('explanation', 'No explanation available.'))

# --- Navigation buttons ---
col1, col2 = st.columns(2)

if col1.button("⬅️ Previous"):
    st.session_state.flash_index = (st.session_state.flash_index - 1) % len(flashcards)

if col2.button("➡️ Next"):
    st.session_state.flash_index = (st.session_state.flash_index + 1) % len(flashcards)