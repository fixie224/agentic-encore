from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def is_user_approved(email: str) -> bool:
    try:
        result = supabase.table("user_profiles").select("is_approved").eq("email", email).single().execute()
        return result.data["is_approved"] if result.data else False
    except Exception as e:
        st.error(f"[Auth Error] {e}")
        return False

def is_admin(email: str) -> bool:
    try:
        result = supabase.table("user_profiles").select("is_admin").eq("email", email).single().execute()
        return result.data["is_admin"] if result.data else False
    except Exception as e:
        st.error(f"[Admin Error] {e}")
        return False