import streamlit as st
import time

st.set_page_config(page_title="XpArena - Pomodoro", page_icon="⏳")

# Initialize state
if 'pomodoro_active' not in st.session_state:
    st.session_state.pomodoro_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'duration' not in st.session_state:
    st.session_state.duration = 25 * 60  # 25 minute default

st.header("⏳ Pomodoro Focus Timer")
col1, col2, col3 = st.columns(3)

# Start Button
if col1.button("Start", key="start"):
    st.session_state.pomodoro_active = True
    st.session_state.start_time = time.time()
    st.session_state.duration = 25 * 60

# Pause Button
if col2.button("Pause", key="pause"):
    st.session_state.pomodoro_active = False

# Reset Button
if col3.button("Reset", key="reset"):
    st.session_state.pomodoro_active = False
    st.session_state.start_time = None
    st.session_state.duration = 25 * 60

# Timer Display
if st.session_state.start_time and st.session_state.pomodoro_active:
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = st.session_state.duration - elapsed
    if remaining <= 0:
        st.session_state.pomodoro_active = False
        st.success("Time's up! Take a break.")
        st.session_state.start_time = None
        remaining = 0
    mins, secs = divmod(remaining, 60)
    st.header(f"{mins:02d}:{secs:02d}")
else:
    mins, secs = divmod(st.session_state.duration, 60)
    st.header(f"{mins:02d}:{secs:02d}")

st.write("You can navigate to another page or keep this open; timer updates on rerun (refresh or whenever another action is taken).")

# Optionally, ask the user to manually refresh to see timer move:
st.info("Timer counts down as long as this session is active. To see it update live, rerun the app or take an action.")
