import streamlit as st
from result_logger_supabase import get_all_results_supabase
import random

st.set_page_config(page_title="🔁 Review Mode", layout="centered")
st.title("🔁 Review Your Mistakes")

# --- Load all results ---
results = get_all_results_supabase()
if not results:
    st.warning("No results available for review.")
    st.stop()

# --- Filter only incorrect answers ---
wrong_results = [r for r in results if not r.get("is_correct", True)]
if not wrong_results:
    st.success("Well done! You have no incorrect answers to review.")
    st.stop()

# --- Shuffle wrong answers ---
random.shuffle(wrong_results)

# --- Review each ---
if "review_index" not in st.session_state:
    st.session_state.review_index = 0

index = st.session_state.review_index
q = wrong_results[index]

st.markdown(f"**Topic:** `{q.get('topic', 'Unknown')}`")
st.markdown(f"**Question:** {q.get('question', 'No question')}")
options = q.get("options", {})

selected = st.radio("Your Options", list(options.items()), format_func=lambda x: f"{x[0]}. {x[1]}")
st.markdown(f"**Correct Answer:** {', '.join(q.get('answer', []))}")
st.info(q.get("explanation", "No explanation provided."))

# --- Navigation ---
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Previous") and index > 0:
        st.session_state.review_index -= 1
with col2:
    if st.button("➡️ Next") and index < len(wrong_results) - 1:
        st.session_state.review_index += 1

st.markdown(f"Question {index + 1} of {len(wrong_results)}")