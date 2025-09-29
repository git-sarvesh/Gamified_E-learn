import streamlit as st
import time
import requests

st.set_page_config(
    page_title="XpArena - Pomodoro & Practice Questions",
    page_icon="⏳",
    layout="centered"
)

# Improved: Sidebar for Gemini API Key entry
with st.sidebar:
    st.markdown("🔑 **Gemini API Key Settings**")
    GEMINI_API_KEY = st.text_input("AIzaSyBCbRPqIfY4ITwEbeuY_tS8Nw6icnvmd34", type='password')
    st.markdown("Powered by Google Gemini AI")

# --- Pomodoro Timer ---
if 'pomodoro_active' not in st.session_state:
    st.session_state.pomodoro_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'duration' not in st.session_state:
    st.session_state.duration = 25 * 60  # 25 minute default

st.markdown("<h1 style='text-align:center;'>⏳ Pomodoro Focus Timer</h1>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,1,1])

with col1:
    if st.button("▶️ Start", key="start", help="Start your Pomodoro focus session"):
        st.session_state.pomodoro_active = True
        st.session_state.start_time = time.time()
        st.session_state.duration = 25 * 60
with col2:
    if st.button("⏸️ Pause", key="pause", help="Pause your Pomodoro session"):
        st.session_state.pomodoro_active = False
with col3:
    if st.button("🔄 Reset", key="reset", help="Reset the timer to start fresh"):
        st.session_state.pomodoro_active = False
        st.session_state.start_time = None
        st.session_state.duration = 25 * 60

# Animation for time up
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
    st.markdown(f"<h2 style='text-align:center;'>{mins:02d}:{secs:02d}</h2>", unsafe_allow_html=True)
else:
    mins, secs = divmod(st.session_state.duration, 60)
    st.markdown(f"<h2 style='text-align:center;'>{mins:02d}:{secs:02d}</h2>", unsafe_allow_html=True)

st.info("Timer counts down as long as this session is active. For live updates, rerun the app or take an action.")

# --- GeminiAI MCQ generator ---
st.divider()
st.markdown("<h1>🧠 Generate Practice Questions (CBSE & State-board)</h1>", unsafe_allow_html=True)

def get_gemini_questions(api_key, subject, language="English"):
    prompt = (
        f"Generate 5 multiple-choice questions for {subject} "
        f"based on the CBSE and state board curriculum in {language}. "
        "For each question, provide 4 options and reveal the correct answer."
    )
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    params = {"key": api_key}
    try:
        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()
        # Gemini's response format may vary, here's a generic parsing
        candidates = response.json().get("candidates", [])
        if candidates:
            text_block = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "No questions generated.")
        else:
            text_block = response.text
        return text_block
    except Exception as e:
        return f"❌ Error: {e}"

with st.form("question_gen"):
    subject = st.selectbox(
        "Select Subject 📚",
        [
            "Mathematics",
            "Science",
            "Social Studies",
            "English",
            "Hindi",
            "Computer Science",
            "Physics",
            "Chemistry",
            "Biology"
        ]
    )
    language = st.selectbox(
        "Select Language 🌐",
        ["English", "Hindi", "Tamil"]
    )
    submitted = st.form_submit_button("Generate Questions", help="Uses Gemini AI to create CBSE/state-board MCQs!")

if submitted:
    if not GEMINI_API_KEY:
        st.error("Please enter your Gemini API key in the sidebar.")
    else:
        with st.spinner("Gemini AI is generating your questions..."):
            results = get_gemini_questions(GEMINI_API_KEY, subject, language)
        st.subheader("📄 Generated Questions")
        with st.expander("Click to view your MCQs"):
            st.code(results, language="markdown")
        st.success("Practice questions created! 📚")

# Interactive bonus: Emoji reactions
if submitted and "Error" not in results:
    st.markdown("😎 Good luck practicing! 🚀")
