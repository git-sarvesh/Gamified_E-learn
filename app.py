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

if "page" not in st.session_state:
    st.session_state.page = "home"
if "chosen_lang" not in st.session_state:
    st.session_state.chosen_lang = "English"

def go(page):
    st.session_state.page = page
if st.session_state.page == "home":
    st.title("🏠 XpArena Home")
    st.markdown("Choose what you'd like to do:")
    col1, col2, col3 = st.columns(3)
    col1.button("⏳ Pomodoro Timer", on_click=go, args=("pomodoro",))
    col2.button("📝 MCQ Quiz", on_click=go, args=("quiz",))
    col3.button("🌐 Change Language", on_click=go, args=("language",))
    st.write(f"Current language: **{st.session_state.chosen_lang}**")
    st.markdown("---")
    st.info("Welcome to XpArena! Boost your focus, play learning games, or study in any Indian language.")
if st.session_state.page == "pomodoro":
    st.markdown("<h1 style='text-align:center;'>⏳ Pomodoro Focus Timer</h1>", unsafe_allow_html=True)
    pomodoro_options = {
        "25 min (Classic)": 25 * 60,
        "50 min (Long)": 50 * 60,
        "15 min (Sprint)": 15 * 60,
        "Custom": None
    }
    chosen_pomo = st.selectbox("Choose your session:", list(pomodoro_options.keys()))
    if chosen_pomo == "Custom":
        custom_time = st.slider("Custom Duration (minutes)", 5, 120, 30)
        st.session_state.duration = custom_time * 60
    else:
        st.session_state.duration = pomodoro_options[chosen_pomo]
    if 'pomodoro_active' not in st.session_state or st.button("🧹 Reset Timer", use_container_width=True):
        st.session_state.pomodoro_active = False
        st.session_state.start_time = None

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.pomodoro_active = True
            st.session_state.start_time = time.time()
            st.session_state.emoji_msg = "🚀 Stay focused!"
    with c2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.pomodoro_active = False
            st.session_state.emoji_msg = "⏸️ Paused. Ready to restart?"
    with c3:
        if st.button("🏠 Home", use_container_width=True):
            go("home")

    st.markdown("---")
    if st.session_state.start_time and st.session_state.pomodoro_active:
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = st.session_state.duration - elapsed
        percent = max(0, remaining) / st.session_state.duration if st.session_state.duration else 0
        if remaining <= 0:
            st.session_state.pomodoro_active = False
            st.success("🎉 Pomodoro complete! Take a short break and come back refreshed! 🍵")
            st.balloons()
            st.session_state.start_time = None
            st.session_state.emoji_msg = "✅ Well done! Ready for another round?"
            remaining = 0
        mins, secs = divmod(max(0, remaining), 60)
        st.markdown(
            f"<h2 style='text-align:center;font-size:3em;'>{mins:02d}:{secs:02d}</h2>",
            unsafe_allow_html=True
        )
        st.progress(percent, text=f"{int(percent*100)}% Focus Time Remaining")
        st.markdown(f"<div style='text-align:center;font-size:1.5em;'>{st.session_state.emoji_msg}</div>", unsafe_allow_html=True)
    else:
        mins, secs = divmod(st.session_state.duration, 60)
        st.markdown(
            f"<h2 style='text-align:center;font-size:3em;'>{mins:02d}:{secs:02d}</h2>",
            unsafe_allow_html=True
        )
        st.info("Set your focus time then click Start to begin your Pomodoro session! 🎯")
if st.session_state.page == "language":
    st.header("🌐 Select Indian Language")
    selected = st.selectbox(
        "Select:", INDIAN_LANGUAGES, index=INDIAN_LANGUAGES.index(st.session_state.chosen_lang)
    )
    ok = st.button("Set Language")
    st.button("🏠 Home", on_click=go, args=("home",))
    if ok:
        st.session_state.chosen_lang = selected
        st.success(f"Language set to {selected}")

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
            r"Q\d*[:.\s-]*(.*?)\nA\)[^\n]+\nB\)[^\n]+\nC\)[^\n]+\nD\)[^\n]+\nAnswer:[\s]*(.)\nExplanation:[\s]*(.*?)\n",
            re.DOTALL
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
            with st.spinner("Questions Being Generated...."):
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
