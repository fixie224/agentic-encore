import streamlit as st
from auth import get_current_user, ensure_user_in_profiles, is_user_approved
from supabase import create_client

# --- Supabase Client ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Catch access_token from redirect ---
params = st.query_params
access_token = params.get("access_token", [None])[0]
refresh_token = params.get("refresh_token", [None])[0]

if access_token and refresh_token:
    try:
        session = supabase.auth.set_session(access_token, refresh_token)
        user = session.user
        if user:
            st.session_state["user_email"] = user.email
            st.session_state["user_id"] = user.id
    except Exception as e:
        st.error(f"Gagal set session: {e}")

# --- Page config ---
st.set_page_config(page_title="Agentic ENCOR Hub", layout="centered")

# --- Supabase Auth Check ---
user = get_current_user()
if user:
    st.session_state["user_email"] = user.email
    ensure_user_in_profiles(user)
    if not is_user_approved(user.email):
        st.warning("⏳ Akaun belum diluluskan. Sila tunggu admin.")
        st.stop()
else:
    st.warning("⚠️ Anda perlu login untuk akses sistem.")
    st.page_link("pages/login.py", label="🔐 Pergi ke Login", icon="🔑")
    st.stop()

# --- Main Page (UI seperti biasa)...git add main.py