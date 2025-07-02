import streamlit as st
from supabase import create_client, Client
import os
import time
import sys

# --- Init Supabase ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="🔐 Login", layout="centered")
st.title("🔐 Login to Agentic ENCOR")

# --- Step 1: Request OTP Email ---
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False

email = st.text_input("📧 Email", placeholder="you@example.com")

if not st.session_state.otp_sent:
    if st.button("📨 Send Magic Link"):
        if not email:
            st.warning("Please enter your email.")
        else:
            try:
                supabase.auth.sign_in_with_otp({"email": email})
                st.session_state.otp_sent = True
                st.success(f"📩 OTP sent to {email}. Please check your email inbox.")
            except Exception as e:
                st.error(f"❌ Failed to send OTP: {e}")
else:
    # --- Step 2: Confirm login session ---
    user = supabase.auth.get_user()
    if user and user.user:
        st.session_state["user_email"] = user.user.email
        st.success(f"✅ Logged in as {user.user.email}")
        st.markdown("Go to the app → [🏠 Home](./app)")
    else:
        st.info("Waiting for you to click the magic link in your email... 🔄")
        time.sleep(5)
        st.experimental_rerun()