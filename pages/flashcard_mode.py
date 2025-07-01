import streamlit as st
from question_bank import load_questions
import random

st.set_page_config(page_title="🧠 Flashcard Mode", layout="centered")
st.title("🧠 Flashcard Study Mode")

# Load all questions
all_questions = load_questions()
all_topics = sorted(set(q['topic'] for q in all_questions))

# Select topic
selected_topic = st.selectbox("📂 Choose Topic:", ["All"] + all_topics)

# Filter questions by topic
if selected_topic == "All":
    flashcards = all_questions
else:
    flashcards = [q for q in all_questions if q['topic'] == selected_topic]

if not flashcards:
    st.info("No flashcards available for selected topic.")
    st.stop()

# Initialize index state
if 'flash_index' not in st.session_state:
    st.session_state.flash_index = 0

# Get current flashcard
q = flashcards[st.session_state.flash_index]

# Display question
st.markdown(f"### 🔖 {q['question']}")

# Reveal answer button
if st.button("🔄 Reveal Answer"):
    st.info("**Answer:** " + ", ".join(q['answer']))
    st.markdown("**Explanation:**")
    st.write(q.get('explanation', 'No explanation available.'))

# Navigation buttons
col1, col2 = st.columns(2)

if col1.button("⬅️ Previous"):
    st.session_state.flash_index = (st.session_state.flash_index - 1) % len(flashcards)

if col2.button("➡️ Next"):
    st.session_state.flash_index = (st.session_state.flash_index + 1) % len(flashcards)