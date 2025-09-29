import streamlit as st
import time
import requests
import re

GEMINI_API_KEY = "AIzaSyBCbRPqIfY4ITwEbeuY_tS8Nw6icnvmd34"

def get_gemini_mcq(api_key, subject, language, num_questions=4):
    prompt = (
        f"Generate {num_questions} multiple-choice questions for {subject} "
        f"as per the {language} CBSE/state board curriculum. "
        "For each question, provide four options A, B, C, D, and the correct answer with a brief explanation. "
        "Format very strictly as:\n"
        "Q: [question text]\nA) [option]\nB) [option]\nC) [option]\nD) [option]\nAnswer: [A/B/C/D]\nExplanation: [explanation]\n"
    )
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    params = {"key": api_key}
    try:
        r = requests.post(url, headers=headers, params=params, json=payload)
        r.raise_for_status()
        candidates = r.json().get("candidates", [])
        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "") if candidates else r.text
        return text
    except Exception as e:
        return f"❌ Error: {e}"

def parse_mcqs(text):
    # Extract MCQs from Gemini result text
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
    # fallback: try to parse at least one question if format differs
    if not results:
        # fallback pattern: looks for loose Q/A without strict formatting
        q_blocks = re.split(r"\nQ[\d]*[:.\s-]*", text)
        for block in q_blocks[1:]:
            try:
                opts = re.findall(r"[A-D]\)[^\n]+", block)
                if len(opts) != 4: continue
                options = [o[2:].strip() for o in opts]
                q_match = block.split('\nA)')[0].strip()
                answer_match = re.search(r"Answer:[\s]*([A-D])", block)
                expl_match = re.search(r"Explanation:[\s]*(.*?)\n", block)
                answer = answer_match.group(1) if answer_match else ""
                expl = expl_match.group(1) if expl_match else ""
                if q_match: results.append({"question": q_match, "options": options, "answer": answer, "explanation": expl})
            except Exception:
                continue
    return results

# --- UI Below ---
st.title("📝 MCQ Quiz")
subject = st.selectbox("Subject", ["Mathematics", "Science", "Social Studies", "English", "Hindi", "Computer Science"])
language = st.selectbox("Language", ["English", "Hindi", "Tamil", "Telugu", "Malayalam"])
num_questions = st.slider("Number of Questions", 1, 10, 4)
generate = st.button("Generate Quiz")

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
            responses.append(
                st.radio(
                    f"Choose for Q{idx+1}", q["options"], index=0, key=f"q{idx}"
                )
            )
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
                correct_num +=1
            else:
                st.error(f"❌ Incorrect. Correct answer: {correct_option}. Explanation: {q['explanation']}")
        st.info(f"You got {correct_num}/{len(mcqs)} correct.")
