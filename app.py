import streamlit as st
import time
import requests

# --- CONFIG: Place your Gemini API Key below ---
GEMINI_API_KEY = "AIzaSyBCbRPqIfY4ITwEbeuY_tS8Nw6icnvmd34"  # <--- Replace with your key

INDIAN_LANGUAGES = [
    "English", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali",
    "Marathi", "Urdu", "Gujarati", "Odia", "Punjabi", "Assamese", "Sanskrit"
]

if "page" not in st.session_state:
    st.session_state.page = "home"
if "chosen_lang" not in st.session_state:
    st.session_state.chosen_lang = "English"

def go(page):
    st.session_state.page = page

# ---- Home Page ----
if st.session_state.page == "home":
    st.title("🎓 XpArena Home")
    st.markdown("Welcome! Choose what you'd like to do:")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("⏳ Pomodoro Focus Timer", on_click=go, args=("pomodoro",))
    with c2:
        st.button("🎮 Games (CBSE & State-board)", on_click=go, args=("games",))
    with c3:
        st.button("🌐 Change Language", on_click=go, args=("lang",))

# ---- Pomodoro Page ----
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

    st.button("🏠 Back to Home", on_click=go, args=("home",))
    st.info("Timer counts down as long as this session is active.")

# ---- Games Page ----
if st.session_state.page == "games":
    st.header("🎮 CBSE & State-board Games")
    game_type = st.selectbox("Choose Game Type", ["MCQ Quiz", "Flashcards", "True/False", "Fill in the Blanks"])
    subject = st.selectbox("Choose Subject", ["Mathematics", "Science", "Social Studies", "English", "Hindi", "Computer Science"])
    language = st.session_state.chosen_lang

    st.button("🏠 Back to Home", on_click=go, args=("home",))

    def get_gemini_questions(api_key, subject, language, game_type):
        prompt = f"Generate {game_type}s for {subject} as per the {language} CBSE/state board curriculum."
        # Use the latest endpoint and model!
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": api_key}
        try:
            r = requests.post(url, headers=headers, params=params, json=payload)
            r.raise_for_status()
            candidates = r.json().get("candidates", [])
            text_block = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "") if candidates else r.text
            return text_block
        except Exception as e:
            return f"❌ Error: {e}"
    if st.button(f"Generate {game_type}"):
        with st.spinner("Generating..."):
            result = get_gemini_questions(GEMINI_API_KEY, subject, language, game_type)
        st.code(result)

# ---- Language Page ----
if st.session_state.page == "lang":
    st.header("🌐 Select Your Preferred Language")
    lang_choice = st.selectbox(
        "Languages:", INDIAN_LANGUAGES,
        index=INDIAN_LANGUAGES.index(st.session_state.chosen_lang))
    if st.button("Set Language"):
        st.session_state.chosen_lang = lang_choice
        st.success(f"Language set to {lang_choice}")
    st.button("🏠 Back to Home", on_click=go, args=("home",))
