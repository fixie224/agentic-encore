from openai import OpenAI
import streamlit as st

# Init OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_encor_question_v1(topic: str = "IP Routing", difficulty: str = "medium") -> dict:
    prompt = (
        f"Buat satu soalan pilihan ganda gaya CCNP ENCOR 350-401 tentang topik '{topic}' "
        f"dengan tahap kesukaran '{difficulty}'. Sertakan 4 pilihan jawapan (A-D), "
        f"jawapan betul (boleh satu atau lebih), dan penjelasan. Formatkan output dalam JSON:\n\n"
        "{\n"
        '  "question": "Soalan anda...",\n'
        '  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},\n'
        '  "answer": ["B"],\n'
        '  "explanation": "Penjelasan jawapan",\n'
        '  "topic": "' + topic + '"\n'
        '}'
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        return eval(content) if isinstance(content, str) else content
    except Exception as e:
        st.error(f"Error generating question: {e}")
        return {}