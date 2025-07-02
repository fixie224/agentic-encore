import streamlit as st
import os, sys
from auth import is_user_approved
from admin import is_admin

# --- Semak Login & Kelulusan ---
email = st.session_state.get("user_email", None)

if not email:
    st.warning("⚠️ Anda perlu login untuk akses halaman ini.")
    st.page_link("pages/login.py", label="🔐 Pergi ke Login", icon="🔑")
    st.stop()

if not is_user_approved(email):
    st.error("❌ Akaun anda belum diluluskan. Sila tunggu kelulusan admin.")
    st.stop()

if is_admin(email):
    st.success("✅ Anda log masuk sebagai admin.")

# --- Sidebar Info ---
with st.sidebar:
    st.markdown(f"👋 Logged in as `{email}`")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Streamlit Page Config ---
st.set_page_config(page_title="🔬 Lab Simulation Mode", layout="centered")
st.title("🔬 CCNP Lab Simulation")

# --- Example Scenario ---
tasks = [
    "1. Enable OSPF on interface Gig0/1",
    "2. Set OSPF process ID to 10",
    "3. Advertise network 10.1.1.0/24 into OSPF"
]

correct_steps = [
    "router ospf 10",
    "network 10.1.1.0 0.0.0.255 area 0",
    "interface GigabitEthernet0/1",
    "ip ospf 10 area 0"
]

st.markdown("### 🛠️ Task:")
for t in tasks:
    st.markdown(f"- {t}")

# --- User Input ---
user_cmds = st.text_area("✍️ Enter your Cisco CLI config (one per line):", height=200)

# --- Submit & Check ---
if st.button("✅ Submit Config"):
    user_lines = [line.strip().lower() for line in user_cmds.strip().split("\n") if line.strip()]
    correct_found = [cmd for cmd in correct_steps if cmd.lower() in user_lines]

    st.success(f"✅ Anda berjaya lengkapkan {len(correct_found)} dari {len(correct_steps)} langkah yang betul.")

    st.markdown("---")
    st.markdown("### 🔍 Semakan Jawapan:")
    for cmd in correct_steps:
        if cmd.lower() in user_lines:
            st.markdown(f"✅ `{cmd}`")
        else:
            st.markdown(f"❌ `{cmd}`")