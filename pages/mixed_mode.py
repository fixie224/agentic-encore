import streamlit as st
import random, time
import openai
import os, sys
from question_bank import load_questions
from quiz_logic import check_answer, get_explanation
from result_logger_supabase import log_result_supabase

# Ensure OpenAI key exists
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# --- CONFIG ---
st.set_page_config(page_title="Mixed Mode Quiz", layout="centered")
st.title("🧠 Mixed Mode: Static + GPT Questions")

# --- Session Init ---
if 'mode' not in st.session_state:
    st.session_state.mode = 'mixed'
if 'shuffled_questions' not in st.session_state:
    all_qs = load_questions()
    random.shuffle(all_qs)
    st.session_state.shuffled_questions = all_qs
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0

# --- Select 80% Static + 20% GPT ---
static_pool = st.session_state.shuffled_questions
use_gpt = (st.session_state.question_index + 1) % 5 == 0

# --- Display Question ---
if use_gpt:
    st.info("📡 GPT-Generated Question")
    topic = "Routing"
    prompt = f"Generate a CCNP ENCOR multiple choice question on the topic: {topic}. Include 1 correct and 3 incorrect options."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Cisco Certified trainer."},
            {"role": "user", "content": prompt}
        ]
    )
    q_text = response.choices[0].message['content']
    st.markdown(f"**GPT Question {st.session_state.question_index+1}:**")
    st.markdown(q_text)
    st.warning("👉 GPT question review not interactive yet.")
else:
    q = static_pool[st.session_state.question_index % len(static_pool)]
    qid = q['id']
    st.markdown(f"### 📘 Topic: {q['topic']}")
    st.subheader(q['question'])

    opts = q['options']
    option_keys = list(opts.keys())
    random.shuffle(option_keys)
    label_map = {f"{k}: {opts[k]}": k for k in option_keys}

    user_selection = st.multiselect(
        "Select answer(s):",
        options=list(label_map.keys()),
        key=f"select_{qid}"
    )
    user_answer = [label_map[sel] for sel in user_selection]

    if st.button("✅ Submit Answer"):
        correct = check_answer(user_answer, q['answer'])
        if correct:
            st.success("✅ Correct!")
            st.session_state.score += 1
        else:
            st.error(f"❌ Incorrect. Correct answer: {', '.join(q['answer'])}")
        with st.expander("💡 Explanation"):
            st.write(get_explanation(q))
        log_result_supabase(qid, q['topic'], correct, time.time())

        st.session_state.question_index += 1
        st.rerun()

# --- Score ---
st.markdown("---")
st.info(f"Progress: {st.session_state.question_index} questions attempted.")
st.success(f"✅ Score: {st.session_state.score}")