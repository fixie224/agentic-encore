import streamlit as st
import os, sys
from supabase import create_client

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from admin import is_admin

# --- Setup Supabase ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Page Config ---
st.set_page_config(page_title="👥 Admin User Approval", layout="centered")
st.title("👥 User Approval Dashboard")

# --- Auth Check ---
if "user_email" not in st.session_state:
    st.warning("⚠️ You must log in to access this page.")
    st.page_link("pages/login.py", label="🔐 Go to Login", icon="🔑")
    st.stop()

email = st.session_state["user_email"]
if not is_admin(email):
    st.error("🚫 Unauthorized access. Only admins can view this page.")
    st.stop()

# --- Get all users ---
@st.cache_data(ttl=60)
def get_all_users():
    try:
        response = supabase.table("user_profiles").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"❌ Failed to load users: {e}")
        return []

# --- Update approval status ---
def update_approval(user_id, status):
    try:
        supabase.table("user_profiles").update({"is_approved": status}).eq("user_id", user_id).execute()
        st.success(f"✅ {'Approved' if status else 'Revoked'} successfully.")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"❌ Failed to update: {e}")

# --- Display table ---
users = get_all_users()
if not users:
    st.warning("No users found.")
    st.stop()

for user in users:
    col1, col2, col3 = st.columns([4, 2, 2])
    with col1:
        st.markdown(f"📧 **{user['email']}**")
    with col2:
        st.markdown("✅ Approved" if user["is_approved"] else "❌ Not Approved")
    with col3:
        action = st.selectbox(
            "Action", 
            options=["-", "Approve", "Revoke"],
            key=f"action_{user['user_id']}"
        )
        if action == "Approve" and not user["is_approved"]:
            update_approval(user["user_id"], True)
        elif action == "Revoke" and user["is_approved"]:
            update_approval(user["user_id"], False)

st.info("✅ All changes apply immediately.")