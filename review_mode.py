import streamlit as st
import sqlite3
from question_bank import load_questions
from quiz_logic import check_answer, get_explanation
from result_logger_supabase import init_db

st.set_page_config(page_title="🔁 Review Mode", layout="centered")
st.title("🔁 Agentic Encore – Review Incorrect Answers")

# Ensure DB is ready
init_db()

# Get list of wrong attempts
@st.cache_data
def get_incorrect_question_ids():
    conn = sqlite3.connect("data/results.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT question_id 
        FROM results 
        WHERE is_correct = 0
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Load question bank and match
question_bank = load_questions()
wrong_ids = get_incorrect_question_ids()
questions_to_review = [q for q in question_bank if q['id'] in wrong_ids]

if not questions_to_review:
    st.info("🎉 No incorrect answers to review! Good job!")
else:
    st.warning(f"You have {len(questions_to_review)} questions to review.")

    for q in questions_to_review:
        st.markdown(f"### 📘 Topic: {q['topic']}")
        st.subheader(q['question'])

        opts = q['options']
        label_map = {f"{k}: {v}": k for k, v in opts.items()}

        user_selection = st.multiselect(
            f"Select answer(s) for Question {q['id']}",
            options=list(label_map.keys()),
            key=q['id'] + "_review"
        )
        user_answer = [label_map[sel] for sel in user_selection]

        if user_selection:
            if check_answer(user_answer, q['answer']):
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")

            with st.expander("💡 Explanation"):
                st.write(get_explanation(q))