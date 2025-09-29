import streamlit as st
import time
import random

st.set_page_config(page_title="XpArena - Gamified Learning", page_icon=":trophy:")

# Initialize session state
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'show_quiz_result' not in st.session_state:
    st.session_state.show_quiz_result = False
if 'click_score' not in st.session_state:
    st.session_state.click_score = 0
if 'click_game_active' not in st.session_state:
    st.session_state.click_game_active = False
if 'avatar' not in st.session_state:
    st.session_state.avatar = None
if 'pomodoro_running' not in st.session_state:
    st.session_state.pomodoro_running = False
if 'pomodoro_seconds' not in st.session_state:
    st.session_state.pomodoro_seconds = 25*60
if 'on_break' not in st.session_state:
    st.session_state.on_break = False

st.title("🏆 XpArena - Gamified Learning Platform")
st.subheader("Welcome! Level up your learning in a fun way.")

#--- Avatar Selector
avatars = {
    'Girl':'https://i.pravatar.cc/100?img=1',
    'Boy':'https://i.pravatar.cc/100?img=2',
    'Student':'https://i.pravatar.cc/100?img=3',
    'Coder':'https://i.pravatar.cc/100?img=4',
}

with st.expander("Choose Your Avatar", expanded=True):
    cols = st.columns(len(avatars))
    for i, (name, url) in enumerate(avatars.items()):
        if cols[i].button(f"Choose {name}"):
            st.session_state.avatar = url
    if st.session_state.avatar:
        st.image(st.session_state.avatar, width=120, caption="Selected Avatar")

#--- Menu
page = st.sidebar.radio("Select an option", ["Home", "Quiz", "Click Game", "Pomodoro Timer"])

#--- Home
if page == "Home":
    st.header("Gamified Activities")
    st.markdown("""
    - 📋 **Quiz**: Test your knowledge!
    - 👆 **Click Game**: Super simple, super fun.
    - ⏳ **Pomodoro Timer**: Stay focused in study sessions.
    """)

#--- Quiz Game
elif page == "Quiz":
    st.header("📝 Quick Math Quiz")
    quiz = [
        {"question":"What is 25 × 4?", "options":["90","100","110","120"], "answer":"100"},
        {"question":"The value of π (pi) is approximately?", "options": ["2.14", "3.14", "4.14", "3.41"], "answer":"3.14"},
        {"question":"Solve: 12 + 15 × 2 = ?", "options": ["42", "30", "27", "24"], "answer":"42"},
        {"question":"Area of a rectangle with length 5 and breadth 3?", "options":["15","8","10","12"], "answer":"15"},
    ]
    if st.session_state.show_quiz_result:
        st.success(f"Quiz Complete! Your score: {st.session_state.quiz_score}/{len(quiz)}")
        if st.button("Restart Quiz"):
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.show_quiz_result = False
    else:
        q = quiz[st.session_state.quiz_index]
        st.write(f"**Q{st.session_state.quiz_index+1}: {q['question']}**")
        option = st.radio("Choose your answer:", q['options'], key=f"radio_{st.session_state.quiz_index}")
        if st.button("Submit Answer"):
            if option == q["answer"]:
                st.session_state.quiz_score += 1
            st.session_state.quiz_index += 1
            if st.session_state.quiz_index >= len(quiz):
                st.session_state.show_quiz_result = True
            st.experimental_rerun()

#--- Click Game
elif page == "Click Game":
    st.header("👆 Click the Button!")
    st.write("How many times can you click in 10 seconds?")
    if not st.session_state.click_game_active:
        if st.button("Start Game"):
            st.session_state.click_game_active = True
            st.session_state.click_score = 0
            st.session_state.click_start_time = time.time()
            st.experimental_rerun()
    else:
        remaining = 10 - int(time.time() - st.session_state.click_start_time)
        if remaining > 0:
            if st.button("Click me!"):
                st.session_state.click_score += 1
            st.write(f"Time left: {remaining} seconds")
            st.write(f"Score: {st.session_state.click_score}")
            st.experimental_rerun()
        else:
            st.write(f"Game finished! Your score: {st.session_state.click_score}")
            st.session_state.click_game_active = False
            if st.button("Play Again"):
                st.experimental_rerun()

#--- Pomodoro Timer
elif page == "Pomodoro Timer":
    st.header("⏳ Pomodoro Focus Timer")
    timer_placeholder = st.empty()
    status_placeholder = st.empty()
    if st.button("Start") and not st.session_state.pomodoro_running:
        st.session_state.pomodoro_running = True
        if st.session_state.pomodoro_seconds == 0:
            st.session_state.pomodoro_seconds = 25*60 if not st.session_state.on_break else 5*60
    if st.button("Reset"):
        st.session_state.pomodoro_running = False
        st.session_state.pomodoro_seconds = 25*60
        st.session_state.on_break = False

    while st.session_state.pomodoro_running and st.session_state.pomodoro_seconds > 0:
        mins, secs = divmod(st.session_state.pomodoro_seconds, 60)
        timer_placeholder.header(f"{mins:02d}:{secs:02d}")
        status = "Break Time! Relax :)" if st.session_state.on_break else "Work Interval"
        status_placeholder.write(status)
        time.sleep(1)
        st.session_state.pomodoro_seconds -= 1
        st.experimental_rerun()
    else:
        if st.session_state.pomodoro_running and st.session_state.pomodoro_seconds == 0:
            st.session_state.on_break = not st.session_state.on_break
            st.session_state.pomodoro_seconds = 5*60 if st.session_state.on_break else 25*60
            st.session_state.pomodoro_running = False
            st.experimental_rerun()

    mins, secs = divmod(st.session_state.pomodoro_seconds, 60)
    timer_placeholder.header(f"{mins:02d}:{secs:02d}")
    status = "Break Time! Relax :)" if st.session_state.on_break else "Work Interval"
    status_placeholder.write(status)
