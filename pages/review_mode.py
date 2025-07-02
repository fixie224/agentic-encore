import streamlit as st
import random
from result_logger_supabase import get_all_results_supabase
from auth import is_user_approved
from admin import is_admin

# --- Check login session ---
email = st.session_state.get("user_email", None)

if not email:
    st.warning("⚠️ Anda perlu login untuk akses halaman ini.")
    st.page_link("pages/login.py", label="🔐 Pergi ke Login", icon="🔑")
    st.stop()

# --- Check approval ---
if not is_user_approved(email):
    st.error("❌ Akaun anda belum diluluskan.")
    st.stop()

# --- Admin notice ---
if is_admin(email):
    st.success("✅ Anda ialah admin.")

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"👋 Logged in as `{email}`")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Page config ---
st.set_page_config(page_title="🔁 Review Mode", layout="centered")
st.title("🔁 Review Your Mistakes")

# --- Load all results ---
results = get_all_results_supabase()
if not results:
    st.warning("⚠️ No results found. Sila jawab kuiz terlebih dahulu.")
    st.stop()

# --- Filter only incorrect answers ---
wrong_results = [r for r in results if not r.get("is_correct", True)]
if not wrong_results:
    st.success("🎉 Anda tiada jawapan salah untuk disemak.")
    st.stop()

# --- Randomize and setup ---
random.shuffle(wrong_results)

if "review_index" not in st.session_state:
    st.session_state.review_index = 0

index = st.session_state.review_index
q = wrong_results[index]

# --- Show question review ---
st.subheader(f"📘 Topic: {q.get('topic', 'Unknown')}")
st.markdown(f"**Question:** {q.get('question', 'No question text')}")
options = q.get("options", {})

if options:
    st.radio("Your Options:", list(options.items()), format_func=lambda x: f"{x[0]}. {x[1]}", index=0)
else:
    st.warning("⚠️ Options not available for this question.")

# --- Answer & explanation ---
st.markdown(f"**Correct Answer:** {', '.join(q.get('answer', []))}")
st.info(q.get("explanation", "No explanation provided."))

# --- Navigation buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Previous") and index > 0:
        st.session_state.review_index -= 1
        st.experimental_rerun()
with col2:
    if st.button("➡️ Next") and index < len(wrong_results) - 1:
        st.session_state.review_index += 1
        st.experimental_rerun()

st.markdown(f"Question {index + 1} of {len(wrong_results)}")