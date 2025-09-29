import streamlit as st
import time
import requests

st.set_page_config(page_title="XpArena - Pomodoro", page_icon="⏳")

# CONFIG: enter your Gemini API Key here
GEMINI_API_KEY = "AIzaSyBCbRPqIfY4ITwEbeuY_tS8Nw6icnvmd34"

def get_gemini_questions(subject, language="English"):
    prompt = (
        f"Generate 5 multiple-choice questions for {subject} "
        f"based on the CBSE and state board curriculum in {language}.\n"
        "Return questions, 4 options for each, and the correct answer."
    )
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    params = {"key": GEMINI_API_KEY}
    try:
        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()
        # Gemini's response format may vary
        data = response.json()
        # Assuming text result is in data['candidates'][0]['content']['parts'][0]['text']
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "No questions generated.")
        )
        return text
    except Exception as e:
        return f"Error: {e}"

# --- Pomodoro Timer ---
if 'pomodoro_active' not in st.session_state:
    st.session_state.pomodoro_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'duration' not in st.session_state:
    st.session_state.duration = 25 * 60  # 25 minute default

st.header("⏳ Pomodoro Focus Timer")
col1, col2, col3 = st.columns(3)

if col1.button("Start", key="start"):
    st.session_state.pomodoro_active = True
    st.session_state.start_time = time.time()
    st.session_state.duration = 25 * 60

if col2.button("Pause", key="pause"):
    st.session_state.pomodoro_active = False

if col3.button("Reset", key="reset"):
    st.session_state.pomodoro_active = False
    st.session_state.start_time = None
    st.session_state.duration = 25 * 60

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
st.info("Timer counts down as long as this session is active. To see it update live, rerun the app or take an action.")

# --- GeminiAI MCQ generator ---
st.header("🧠 Generate Practice Questions (CBSE & State-board)")
with st.form("question_gen"):
    subject = st.selectbox(
        "Select Subject",
        ["Mathematics", "Science", "English", "Social Studies", "Hindi", "Tamil", "Computer Science"]
    )
    language = st.selectbox(
        "Select Language",
        ["English", "Hindi", "Tamil"]
    )
    submitted = st.form_submit_button("Generate Questions")

if submitted:
    with st.spinner("Generating questions..."):
        results = get_gemini_questions(subject, language)
    st.subheader("Generated Questions")
    st.code(results)
