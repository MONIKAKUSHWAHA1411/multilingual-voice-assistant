import streamlit as st
import whisper
import tempfile
import os
from gtts import gTTS
from openai import OpenAI
from st_audiorec import st_audiorec

# -------------------------------------------------
# Page Config + UI Polish
# -------------------------------------------------
st.set_page_config(
    page_title="Multilingual Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

st.markdown(
    """
    <style>
    .block-container { max-width: 820px; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎙 Multilingual Voice Assistant")
st.write(
    "Talk directly using the mic 🎙️ or upload recorded calls for analysis (English / Hindi / Hinglish)."
)

# -------------------------------------------------
# OpenAI Client
# -------------------------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------------------------------
# LLM-Based Intent Classification
# -------------------------------------------------
def llm_intent_classification(user_text: str) -> dict:
    system_prompt = """
You are an enterprise Indian banking voice assistant.

Classify the user's query into ONE of the following intents:
1. Account Balance
2. Transaction History
3. Card Block / Lost Card
4. Account Conversion / Account Type Change
5. Card Eligibility / Replacement
6. Fees & Charges
7. General Banking Query

Respond strictly in JSON with keys:
- intent
- reasoning
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    )

    return eval(response.choices[0].message.content)

# -------------------------------------------------
# BFSI Response Generation
# -------------------------------------------------
def generate_bfsi_response(intent: str, user_text: str) -> str:
    system_prompt = """
You are a compliant Indian banking voice assistant.
Rules:
- Do not give financial advice
- Do not promise approvals
- Keep response short, clear, professional
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
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
        ]
    )

    return response.choices[0].message.content.strip()

# -------------------------------------------------
# Voice Reply (TTS)
# -------------------------------------------------
def generate_voice_reply(text: str, lang: str):
    tts_lang = "hi" if lang == "hi" else "en"
    tts = gTTS(text=text, lang=tts_lang)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
        tts.save(audio_file.name)
        return audio_file.name

# -------------------------------------------------
# Audio Processing (shared)
# -------------------------------------------------
def process_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        audio_path = tmp.name

    whisper_model = whisper.load_model("base")
    result = whisper_model.transcribe(audio_path)
    os.remove(audio_path)

    return result["text"], result["language"]

# -------------------------------------------------
# INPUT SECTION
# -------------------------------------------------
st.divider()
st.markdown("## 🎧 Input Options")

# 🎙️ Mic Input
st.markdown("### 🎙️ Speak now")
audio_bytes = st_audiorec()

# 📂 File Upload
st.markdown("### 📂 Upload recorded call")
uploaded_file = st.file_uploader(
    "Upload WAV or MP3 file",
    type=["wav", "mp3"]
)

# -------------------------------------------------
# Determine Audio Source
# -------------------------------------------------
final_audio = None

if audio_bytes is not None:
    final_audio = audio_bytes
    st.success("Voice recorded successfully")

elif uploaded_file is not None:
    final_audio = uploaded_file.read()
    st.success("Audio file uploaded successfully")

# -------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------
if final_audio:
    st.divider()
    st.info("🎧 Processing audio…")

    user_text, language = process_audio(final_audio)

    # -----------------------------
    # User Query
    # -----------------------------
    st.markdown("### 🗣️ User Query")
    st.markdown(
        f"""
        <div style="background:#1f2937;padding:16px;border-radius:12px;">
        {user_text}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f"🌍 **Detected Language:** `{language}`")

    st.divider()

    # -----------------------------
    # Intent Understanding
    # -----------------------------
    with st.spinner("🧠 Understanding intent and context…"):
        intent_data = llm_intent_classification(user_text)

    st.markdown("### 🧠 AI Understanding")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Intent", intent_data["intent"])
    with col2:
        st.metric("Confidence", "High")

    st.info(intent_data["reasoning"])

    st.divider()

    # -----------------------------
    # Response
    # -----------------------------
    with st.spinner("💬 Generating response…"):
        response_text = generate_bfsi_response(
            intent_data["intent"],
            user_text
        )

    st.markdown("### 🤖 Assistant Response")
    st.markdown(
        f"""
        <div style="background:#111827;padding:18px;border-radius:14px;line-height:1.6;">
        {response_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------
    # Voice Reply
    # -----------------------------
    voice_path = generate_voice_reply(response_text, language)
    st.markdown("### 🔊 Voice Reply")
    st.audio(voice_path)
    os.remove(voice_path)
