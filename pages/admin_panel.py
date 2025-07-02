import streamlit as st
from supabase import create_client
import sys, os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth import is_user_approved
from admin import is_admin

# --- Supabase Client ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Page Config ---
st.set_page_config(page_title="🛠️ Admin Panel", layout="centered")
st.title("🛠️ Admin Panel - User Management")

# --- Auth Check ---
if "user_email" not in st.session_state:
    st.warning("⚠️ Anda perlu login untuk akses halaman ini.")
    st.page_link("pages/login.py", label="🔐 Pergi ke Login", icon="🔑")
    st.stop()

email = st.session_state["user_email"]
if not is_admin(email):
    st.error("🚫 Unauthorized access. Only admin allowed.")
    st.stop()

# --- Load user_profiles ---
try:
    response = supabase.table("user_profiles").select("*").execute()
    users = response.data or []
except Exception as e:
    st.error(f"❌ Failed to load users: {e}")
    st.stop()

if not users:
    st.info("No users found.")
    st.stop()

# --- Display Users ---
for user in users:
    st.markdown(f"**📧 Email:** `{user['email']}`")
    st.write(f"✅ Approved: `{user['is_approved']}`")

    col1, col2 = st.columns(2)
    with col1:
        if not user["is_approved"]:
            if st.button("✅ Approve", key=f"approve_{user['user_id']}"):
                supabase.table("user_profiles").update({"is_approved": True}).eq("user_id", user["user_id"]).execute()
                st.success(f"{user['email']} approved!")
                st.experimental_rerun()

    with col2:
        if st.button("🗑️ Delete (Manual)", key=f"delete_{user['user_id']}"):
            st.warning("⚠️ Use Supabase dashboard to delete user from auth.users.")

    st.markdown("---")