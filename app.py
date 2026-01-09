import streamlit as st
import whisper
import tempfile
import os
from gtts import gTTS
import openai

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Multilingual Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙 Multilingual Voice Assistant")
st.write("Upload an audio file (English / Hindi / Hinglish)")

# -----------------------------
# OpenAI API Key (Streamlit Secrets)
# -----------------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# -----------------------------
# LLM-Based Intent Detection
# -----------------------------
def llm_intent_classification(user_text: str) -> dict:
    system_prompt = """
You are an enterprise banking voice assistant.
Classify the user's query into one of the following intents:

1. Account Balance
2. Transaction History
3. Card Block / Lost Card
4. Account Conversion / Account Type Change
5. Card Eligibility / Replacement
6. Fees & Charges
7. General Banking Query

Return a JSON with:
- intent
- reasoning (short explanation)
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0.2
    )

    return eval(response.choices[0].message.content)

# -----------------------------
# BFSI-Compliant Response Generation
# -----------------------------
def generate_bfsi_response(intent: str, user_text: str) -> str:
    system_prompt = """
You are a compliant Indian banking voice assistant.
Rules:
- Do NOT give financial advice
- Do NOT promise approvals
- Keep tone professional, clear, human
- Short response
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""
User query: {user_text}
Detected intent: {intent}
Generate a helpful response.
"""
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()

# -----------------------------
# Voice Reply (TTS)
# -----------------------------
def generate_voice(text: str, lang: str):
    tts = gTTS(text=text, lang="hi" if lang == "hi" else "en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
        tts.save(audio_file.name)
        return audio_file.name

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload audio file",
    type=["wav", "mp3"]
)

# -----------------------------
# Processing
# -----------------------------
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        audio_path = tmp.name

    st.info("Transcribing audio…")

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    os.remove(audio_path)

    user_text = result["text"]
    language = result["language"]

    st.subheader("📝 Transcription")
    st.write(user_text)

    st.subheader("🌍 Detected Language")
    st.write(language)

    with st.spinner("Understanding intent…"):
        intent_data = llm_intent_classification(user_text)

    st.subheader("🧠 Detected Intent")
    st.write(intent_data["intent"])

    st.subheader("🔍 Reasoning")
    st.write(intent_data["reasoning"])

    with st.spinner("Generating response…"):
        response_text = generate_bfsi_response(intent_data["intent"], user_text)

    st.subheader("💬 Assistant Response")
    st.write(response_text)

    voice_path = generate_voice(response_text, language)

    st.subheader("🔊 Voice Reply")
    st.audio(voice_path)

    os.remove(voice_path)
