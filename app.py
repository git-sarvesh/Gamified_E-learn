import streamlit as st
import time
import requests
import re

GEMINI_API_KEY = "AIzaSyBCbRPqIfY4ITwEbeuY_tS8Nw6icnvmd34"

INDIAN_LANGUAGES = [
    "English", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali",
    "Marathi", "Urdu", "Gujarati", "Odia", "Punjabi", "Assamese", "Sanskrit", 
    "Konkani", "Manipuri", "Santali", "Kashmiri", "Dogri", "Maithili", "Bodo"
]

# Navigation session states
if "page" not in st.session_state:
    st.session_state.page = "home"
if "chosen_lang" not in st.session_state:
    st.session_state.chosen_lang = "English"

def go(page): st.session_state.page = page

# ------ HOME PAGE ------
if st.session_state.page == "home":
    st.title("🏠 XpArena Home")
    st.markdown("Choose what you'd like to do:")
    col1, col2, col3 = st.columns(3)
    col1.button("⏳ Pomodoro Timer", on_click=go, args=("pomodoro",))
    col2.button("📝 MCQ Quiz", on_click=go, args=("quiz",))
    col3.button("🌐 Change Language", on_click=go, args=("language",))
    st.write(f"Current language: **{st.session_state.chosen_lang}**")

# ------ POMODORO ------
if st.session_state.page == "pomodoro":
    st.header("⏳ Pomodoro Focus Timer")
    col1, col2, col3 = st.columns(3)
    if 'pomodoro_active' not in st.session_state:
        st.session_state.pomodoro_active = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'duration' not in st.session_state:
        st.session_state.duration = 25 * 60
    col1.button("▶️ Start", on_click=lambda: setattr(st.session_state, "pomodoro_active", True))
    col2.button("⏸️ Pause", on_click=lambda: setattr(st.session_state, "pomodoro_active", False))
    col3.button("🔄 Reset", on_click=lambda: st.session_state.update({"pomodoro_active": False, "start_time": None, "duration": 25 * 60}))
    if st.session_state.start_time and st.session_state.pomodoro_active:
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = st.session_state.duration - elapsed
        if remaining <= 0:
            st.session_state.pomodoro_active = False
            st.balloons()
            st.success("⏰ Time's up! Take a break!")
            st.session_state.start_time = None
            remaining = 0
        mins, secs = divmod(remaining, 60)
        st.header(f"{mins:02d}:{secs:02d}")
    else:
        mins, secs = divmod(st.session_state.duration, 60)
        st.header(f"{mins:02d}:{secs:02d}")
    st.button("🏠 Home", on_click=go, args=("home",))

# ------ LANGUAGE SELECT ------
if st.session_state.page == "language":
    st.header("🌐 Select Indian Language")
    selected = st.selectbox("Select:", INDIAN_LANGUAGES, index=INDIAN_LANGUAGES.index(st.session_state.chosen_lang))
    ok = st.button("Set Language")
    st.button("🏠 Home", on_click=go, args=("home",))
    if ok:
        st.session_state.chosen_lang = selected
        st.success(f"Language set to {selected}")

# ------ QUIZ ------
if st.session_state.page == "quiz":
    st.header("📝 MCQ Quiz")
    subject = st.selectbox("Subject", ["Mathematics", "Science", "Social Studies", "English", "Hindi", "Computer Science"])
    language = st.session_state.chosen_lang
    num_questions = st.slider("Number of Questions", 1, 10, 4)
    generate = st.button("Generate Quiz")
    st.button("🏠 Home", on_click=go, args=("home",))

    def get_gemini_mcq(api_key, subject, language, num_questions=4):
        prompt = (
            f"Generate {num_questions} multiple-choice questions for {subject} as per the {language} CBSE/state board curriculum. "
            "For each question, provide four options A, B, C, D, and the correct answer with a brief explanation. "
            "Format strictly as:\n"
            "Q: [question text]\nA) [option]\nB) [option]\nC) [option]\nD) [option]\nAnswer: [A/B/C/D]\nExplanation: [explanation]\n"
        )
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": api_key}
        r = requests.post(url, headers=headers, params=params, json=payload)
        r.raise_for_status()
        candidates = r.json().get("candidates", [])
        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "") if candidates else r.text
        return text

    def parse_mcqs(text):
        mcq_pattern = re.compile(
            r"Q\d*[:.\s-]*(.*?)\nA\)[^\n]+\nB\)[^\n]+\nC\)[^\n]+\nD\)[^\n]+\nAnswer:[\s]*(.)\nExplanation:[\s]*(.*?)\n", re.DOTALL
        )
        results = []
        for match in mcq_pattern.finditer(text):
            qtext = match.group(1).strip()
            options = [re.search(f"{opt}\)([^\n]+)", match.group(0)).group(1).strip() for opt in "ABCD"]
            answer = match.group(2).strip()
            expl = match.group(3).strip()
            results.append({"question": qtext, "options": options, "answer": answer, "explanation": expl})
        return results

    if generate or st.session_state.get("mcqs"):
        if generate:
            with st.spinner("Getting questions from Gemini..."):
                mcq_text = get_gemini_mcq(GEMINI_API_KEY, subject, language, num_questions)
                mcqs = parse_mcqs(mcq_text)
                st.session_state.mcqs = mcqs
                st.session_state.submitted = False
        else:
            mcqs = st.session_state.mcqs

        responses = []
        quiz_form = st.form("quiz_form")
        with quiz_form:
            st.header("Choose your answers:")
            for idx, q in enumerate(mcqs):
                st.write(f"**Q{idx+1}: {q['question']}**")
                responses.append(st.radio(f"Choose for Q{idx+1}", q["options"], index=0, key=f"q{idx}"))
            submitted = st.form_submit_button("Submit Answers")

        if submitted or st.session_state.get("submitted"):
            st.session_state.submitted = True
            st.header("Results & Explanations")
            correct_num = 0
            for idx, q in enumerate(mcqs):
                st.write(f"**Q{idx+1}: {q['question']}**")
                st.write(f"- Your answer: **{responses[idx]}**")
                correct_option = q["options"][ord(q['answer']) - ord('A')]
                if responses[idx] == correct_option:
                    st.success(f"✅ Correct! Explanation: {q['explanation']}")
                    correct_num += 1
                else:
                    st.error(f"❌ Incorrect. Correct answer: {correct_option}. Explanation: {q['explanation']}")
            st.info(f"You got {correct_num}/{len(mcqs)} correct.")
