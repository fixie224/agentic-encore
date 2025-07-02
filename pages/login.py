import streamlit as st
from supabase import create_client
import os

# --- Setup Supabase ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="🔐 Login", layout="centered")
st.title("🔐 Login with Email")

# --- Step 1: Masukkan emel untuk magic link login ---
email = st.text_input("📧 Masukkan emel anda")

if st.button("Hantar Magic Link"):
    if email:
        try:
            supabase.auth.sign_in_with_otp({"email": email})
            st.success("✅ Sila semak emel anda untuk pautan login.")
        except Exception as e:
            st.error(f"❌ Gagal hantar link: {e}")
    else:
        st.warning("⚠️ Masukkan emel dahulu.")

# --- Step 2: Selepas redirect dari magic link ---
params = st.query_params
access_token = params.get("access_token", [None])[0]
refresh_token = params.get("refresh_token", [None])[0]

if access_token and refresh_token:
    try:
        session = supabase.auth.set_session(access_token, refresh_token)
        user = session.user

        if user and user.email:
            st.session_state["user_email"] = user.email
            st.session_state["user_id"] = user.id

            # Insert to user_profiles if not exists
            try:
                existing = supabase.table("user_profiles").select("*").eq("user_id", user.id).execute()
                if not existing.data:
                    supabase.table("user_profiles").insert({
                        "user_id": user.id,
                        "email": user.email,
                        "is_approved": False
                    }).execute()
            except Exception as e:
                st.error(f"⚠️ Failed to update user_profiles: {e}")

            st.success("✅ Login berjaya!")
            st.switch_page("app.py")

        else:
            st.error("⚠️ Login gagal — pengguna tidak sah.")
    except Exception as e:
        st.error(f"❌ Session error: {e}")