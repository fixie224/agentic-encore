# auth.py
from supabase import create_client
import streamlit as st

# --- Supabase Setup ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_current_user():
    """Get the currently authenticated Supabase user."""
    try:
        return supabase.auth.get_user().user
    except Exception:
        return None

def ensure_user_in_profiles(user):
    """Ensure the user exists in user_profiles; if not, insert them."""
    user_id = user.id
    email = user.email

    existing = supabase.table("user_profiles").select("user_id").eq("user_id", user_id).execute()

    if not existing.data:
        supabase.table("user_profiles").insert({
            "user_id": user_id,
            "email": email,
            "is_approved": False,
            "is_admin": False
        }).execute()

def is_user_approved(email):
    """Return True if the user is approved, False otherwise."""
    result = supabase.table("user_profiles").select("is_approved").eq("email", email).execute()
    if result.data and len(result.data) > 0:
        return result.data[0].get("is_approved", False)
    return False

def is_admin(email):
    """Return True if the user is admin, False otherwise."""
    result = supabase.table("user_profiles").select("is_admin").eq("email", email).execute()
    if result.data and len(result.data) > 0:
        return result.data[0].get("is_admin", False)
    return False

def require_login_and_approval():
    """Call this early in any page that requires login + approval."""
    user = get_current_user()
    if not user:
        st.warning("Sila login dahulu.")
        st.stop()

    # Save email ke session
    st.session_state["user_email"] = user.email

    # Ensure user profile exists
    ensure_user_in_profiles(user)

    # Check approval
    if not is_user_approved(user.email):
        st.warning("Akaun belum diluluskan. Sila tunggu admin.")
        st.stop()

    return user.email