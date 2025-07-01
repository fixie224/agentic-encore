import streamlit as st

st.set_page_config(page_title="🔬 Lab Simulation Mode", layout="centered")
st.title("🔬 CCNP Lab Simulation")

# Example scenario
tasks = [
    "1. Enable OSPF on interface Gig0/1",
    "2. Set OSPF process ID to 10",
    "3. Advertise network 10.1.1.0/24 into OSPF"
]

# Expected correct steps
correct_steps = [
    "router ospf 10",
    "network 10.1.1.0 0.0.0.255 area 0",
    "interface GigabitEthernet0/1",
    "ip ospf 10 area 0"
]

st.markdown("### 🛠️ Task:")
for t in tasks:
    st.markdown(f"- {t}")

# User input area
user_cmds = st.text_area("✍️ Enter your Cisco CLI config (one per line):", height=200)

# Submit and evaluate
if st.button("✅ Submit Config"):
    user_lines = [line.strip().lower() for line in user_cmds.strip().split("\n") if line.strip()]
    correct_found = [cmd for cmd in correct_steps if cmd.lower() in user_lines]

    st.success(f"✅ You got {len(correct_found)} / {len(correct_steps)} steps correct")

    st.markdown("---")
    st.markdown("### 🔍 Expected Config:")
    for cmd in correct_steps:
        if cmd.lower() in user_lines:
            st.markdown(f"✅ `{cmd}`")
        else:
            st.markdown(f"❌ `{cmd}`")