import streamlit as st
import whisper
import tempfile
import os
from gtts import gTTS
from openai import OpenAI
from st_audiorec import st_audiorec

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Multilingual Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# -------------------------------------------------
# Oriserve-inspired UI (CSS)
# -------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
    color: #e5e7eb;
}

.block-container {
    max-width: 820px;
    padding-top: 2rem;
}

h1, h2, h3 {
    font-weight: 600;
}

.card {
    background: #020617;
    border-radius: 12px;
    padding: 16px 18px;
    border: 1px solid #1e293b;
    margin-top: 8px;
}

button {
    font-size: 13px !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] {
    background: #020617;
    border-radius: 12px;
    border: 1px dashed #334155;
    padding: 12px;
}

[data-testid="metric-container"] {
    background: #020617;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #1e293b;
}

audio {
    width: 100%;
    margin-top: 6px;
}

hr {
    border: none;
    border-top: 1px solid #1e293b;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("🎙 Multilingual Voice Assistant")
st.caption(
    "Voice-first AI for BFSI use cases — talk live or upload recorded customer calls "
    "(English / Hindi / Hinglish)."
)

# -------------------------------------------------
# OpenAI Client
# -------------------------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------------------------------
# LLM Intent Classification
# -------------------------------------------------
def llm_intent_classification(user_text: str) -> dict:
    system_prompt = """
You are an enterprise Indian banking voice assistant.

Classify the user's query into ONE intent:
1. Account Balance
2. Transaction History
3. Card Block / Lost Card
4. Account Conversion / Account Type Change
5. Card Eligibility / Replacement
6. Fees & Charges
7. General Banking Query

Respond strictly in JSON:
{ "intent": "...", "reasoning": "..." }
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
# BFSI-safe Response
# -------------------------------------------------
def generate_bfsi_response(intent: str, user_text: str) -> str:
    system_prompt = """
You are a compliant Indian banking assistant.
Rules:
- No financial advice
- No guarantees
- Clear, professional, short responses
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
# Text-to-Speech
# -------------------------------------------------
def generate_voice_reply(text: str, lang: str):
    tts_lang = "hi" if lang == "hi" else "en"
    tts = gTTS(text=text, lang=tts_lang)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        return f.name

# -------------------------------------------------
# Whisper Processing
# -------------------------------------------------
def process_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        audio_path = tmp.name

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    os.remove(audio_path)

    return result["text"], result["language"]

# -------------------------------------------------
# INPUT OPTIONS
# -------------------------------------------------
st.divider()
st.markdown("## 🎧 Input Options")
st.caption("Speak directly or upload recorded calls for review")

st.markdown("### 🎙️ Speak now")
st.caption("Click Start Recording → Speak → Stop")
mic_audio = st_audiorec()

st.markdown("### 📂 Upload recorded call")
uploaded_file = st.file_uploader(
    "Upload WAV or MP3 file",
    type=["wav", "mp3"]
)

final_audio = None
if mic_audio is not None:
    final_audio = mic_audio
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

    # User Query
    st.markdown("### 🗣️ User Query")
    st.markdown(f"<div class='card'>{user_text}</div>", unsafe_allow_html=True)
    st.caption(f"🌍 Detected language: {language}")

    st.divider()

    # Intent
    with st.spinner("🧠 Understanding intent…"):
        intent_data = llm_intent_classification(user_text)

    st.markdown("### 🧠 AI Understanding")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Intent", intent_data["intent"])
    with col2:
        st.metric("Confidence", "High")

    st.markdown(f"<div class='card'>{intent_data['reasoning']}</div>", unsafe_allow_html=True)

    st.divider()

    # Response
    with st.spinner("💬 Generating response…"):
        response_text = generate_bfsi_response(
            intent_data["intent"],
            user_text
        )

    st.markdown("### 🤖 Assistant Response")
    st.markdown(f"<div class='card'>{response_text}</div>", unsafe_allow_html=True)

    st.divider()

    # Voice Reply
    voice_path = generate_voice_reply(response_text, language)
    st.markdown("### 🔊 Voice Reply")
    st.audio(voice_path)
    os.remove(voice_path)

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        font-size:13px;
        color:#94a3b8;
        padding:24px 0;
        line-height:1.6;
    ">
        Made by 
        <a href="https://www.linkedin.com/in/monika-kushwaha-52443735/"
           target="_blank"
           style="color:#60a5fa; text-decoration:none; font-weight:500;">
           Monika Kushwaha
        </a>
        <br/>
        <span style="font-size:12px; color:#64748b;">
            Built for BFSI Voice AI
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

