import streamlit as st
import time
import requests

# --- CONFIG ---
LANGUAGES = [
    "English", "Hindi", "Tamil", "Telugu", "Bengali", "Marathi", "Gujarati",
    "Kannada", "Malayalam", "Punjabi", "Odia", "Assamese", "Urdu", "Sanskrit"
]
GAMES = [
    "MCQ Quiz",
    "Flashcards",
    "Match The Following",
    "Fill in the Blanks",
    "True/False",
]

# --- SIDEBAR: Gemini API Key ---
with st.sidebar:
    st.markdown("🔑 **Gemini API Key Settings**")
    GEMINI_API_KEY = st.text_input("AIzaSyBCbRPqIfY4ITwEbeuY_tS8Nw6icnvmd34", type='password')
    st.selectbox("🌐 Choose Language", LANGUAGES, key="chosen_lang")

# --- NAVIGATION PAGES ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

def nav(page):
    st.session_state.page = page

# --- HOME PAGE ---
if st.session_state.page == "home":
    st.title("🏠 XpArena Home")
    st.image("https://static.wixstatic.com/media/88a138_9989fa6b9bde49e3b5a8a7b14541e335~mv2.png/v1/crop/x_0,y_0,w_1152,h_768/fill/w_560,h_373,al_c,q_85,usm_0.66_1.00_0.01/88a138_9989fa6b9bde49e3b5a8a7b14541e335~mv2.webp", width=220)
    st.markdown("Welcome! Choose a module to get started:")
    col1, col2 = st.columns(2)
    with col1:
        st.button("⏳ Pomodoro Focus Timer", on_click=nav, args=("pomodoro",), use_container_width=True)
    with col2:
        st.button("🎮 Study Games", on_click=nav, args=("games",), use_container_width=True)
    st.write("Change language anytime from sidebar.")

# --- POMODORO TIMER PAGE ---
if st.session_state.page == "pomodoro":
    st.header("⏳ Pomodoro Focus Timer")
    col1, col2, col3 = st.columns([1,1,1])
    if 'pomodoro_active' not in st.session_state:
        st.session_state.pomodoro_active = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'duration' not in st.session_state:
        st.session_state.duration = 25 * 60

    with col1:
        if st.button("▶️ Start", key="start_tt"):
            st.session_state.pomodoro_active = True
            st.session_state.start_time = time.time()
            st.session_state.duration = 25 * 60
    with col2:
        if st.button("⏸️ Pause", key="pause_tt"):
            st.session_state.pomodoro_active = False
    with col3:
        if st.button("🔄 Reset", key="reset_tt"):
            st.session_state.pomodoro_active = False
            st.session_state.start_time = None
            st.session_state.duration = 25 * 60

    if st.session_state.start_time and st.session_state.pomodoro_active:
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = st.session_state.duration - elapsed
        if remaining <= 0:
            st.session_state.pomodoro_active = False
            st.balloons()
            st.success("⏰ Time's up! Take a break. 🎉")
            st.session_state.start_time = None
            remaining = 0
        mins, secs = divmod(remaining, 60)
        st.header(f"{mins:02d}:{secs:02d}")
    else:
        mins, secs = divmod(st.session_state.duration, 60)
        st.header(f"{mins:02d}:{secs:02d}")

    st.button("🏠 Back to Home", on_click=nav, args=("home",), use_container_width=True)
    st.info("Timer counts down as long as this session is active. For updates, rerun the app or take an action.")

# --- STUDY GAMES PAGE ---
if st.session_state.page == "games":
    st.title("🎮 Study Games & Practice")
    st.markdown("Select a game type and subject to generate CBSE/State-board content using GeminiAI!")
    game_type = st.selectbox("Choose a game", GAMES)
    subject = st.selectbox("Choose Subject", [
        "Mathematics", "Science", "Social Studies", "English",
        "Hindi", "Computer Science", "Physics", "Chemistry", "Biology"
    ])
    language = st.session_state.chosen_lang

    st.button("🏠 Back to Home", on_click=nav, args=("home",), use_container_width=True)

    def get_gemini_questions(api_key, subject, language, game_type):
        prompt = f"Generate {game_type} questions for {subject} based on the {language} CBSE/state board curriculum. Give results in simple text."
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": api_key}
        try:
            r = requests.post(url, headers=headers, params=params, json=payload)
            r.raise_for_status()
            candidates = r.json().get("candidates", [])
            if candidates:
                text_block = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "No questions generated.")
            else:
                text_block = r.text
            return text_block
        except Exception as e:
            return f"❌ Error: {e}"

    if st.button(f"Generate {game_type}", type="primary", use_container_width=True):
        if not GEMINI_API_KEY:
            st.error("Please enter your Gemini API key in the sidebar.")
        else:
            with st.spinner("Gemini AI is generating your game content..."):
                results = get_gemini_questions(GEMINI_API_KEY, subject, language, game_type)
            st.subheader(f"📝 {game_type} for {subject} ({language})")
            st.code(results, language="markdown")
            st.success("Here are your practice items!")

# --- END ---
