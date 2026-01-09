import streamlit as st
import tempfile
import time
from langdetect import detect
from gtts import gTTS
from openai import OpenAI
import google.generativeai as genai

# ==================================================
# Page Config
# ==================================================
st.set_page_config(
    page_title="BFSI Multilingual Voice Assistant",
    layout="centered"
)

# ==================================================
# Session Guards (Rate-limit + caching)
# ==================================================
if "last_call_time" not in st.session_state:
    st.session_state.last_call_time = 0

if "cached_result" not in st.session_state:
    st.session_state.cached_result = None

# ==================================================
# Oriserve-style UI CSS
# ==================================================
st.markdown("""
<style>
body { background-color:#0b1220; }
.header {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    padding:22px;
    border-radius:14px;
    text-align:center;
    margin-bottom:25px;
}
.header h1 {
    font-size:26px;
    color:white;
    margin-bottom:6px;
}
.header p {
    color:#dbeafe;
    font-size:13px;
}
.intent-box {
    background:#020617;
    padding:12px;
    border-radius:10px;
    font-size:14px;
}
.small { font-size:13px; color:#94a3b8; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# Header
# ==================================================
st.markdown("""
<div class="header">
    <h1>🎙️ BFSI Multilingual Voice Assistant</h1>
    <p>Purpose-built Voice AI for Banking & Financial Services</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# API Clients
# ==================================================
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# ==================================================
# BFSI Intent Taxonomy (20+)
# ==================================================
INTENTS = {
    "Account Balance Inquiry": ["balance", "kitna", "remaining"],
    "Mini Statement": ["mini statement", "last transactions"],
    "Card Block": ["block card", "lost card"],
    "Card Replacement": ["replace card", "new card"],
    "PIN Reset": ["forgot pin", "reset pin"],
    "Loan Eligibility": ["loan eligibility", "can i get loan"],
    "Loan EMI": ["emi", "monthly installment"],
    "Loan Foreclosure": ["close loan"],
    "Interest Rates": ["interest rate", "roi"],
    "Account Conversion": ["salary account", "convert account"],
    "KYC Update": ["kyc update"],
    "Debit Card Charges": ["debit card charges"],
    "Credit Limit": ["credit limit"],
    "Transaction Failure": ["failed transaction"],
    "UPI Issue": ["upi issue"],
    "Cheque Status": ["cheque status"],
    "Branch Info": ["nearest branch"],
    "Customer Support": ["talk to agent"],
    "Account Closure": ["close account"],
    "Nominee Update": ["add nominee"],
    "Address Update": ["change address"]
}

def detect_intent(text):
    t = text.lower()
    for intent, keys in INTENTS.items():
        if any(k in t for k in keys):
            return intent
    return "General Banking Query"

# ==================================================
# Speech-to-Text (OpenAI)
# ==================================================
def transcribe(audio_path):
    with open(audio_path, "rb") as audio:
        transcript = openai_client.audio.transcriptions.create(
            file=audio,
            model="gpt-4o-transcribe"
        )
    return transcript.text

# ==================================================
# Gemini LLM Reply
# ==================================================
def generate_reply(text, intent, lang):
    prompt = f"""
You are a BFSI virtual assistant.

User language: {lang}
Detected intent: {intent}

Rules:
- Be polite and professional
- Follow banking compliance tone
- Do NOT expose sensitive customer data
- Keep response concise and helpful

User query:
{text}
"""
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# ==================================================
# Text-to-Speech
# ==================================================
def speak(text, lang):
    tts = gTTS(text=text, lang="hi" if lang == "hi" else "en")
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    tts.save(path)
    return path

# ==================================================
# Input Options
# ==================================================
st.markdown("## 🎧 Input Options")

mic_audio = st.audio_input("🎙️ Speak now")

uploaded_file = st.file_uploader(
    "📁 Upload recorded call (WAV / MP3)",
    type=["wav", "mp3"]
)

if st.button("🔄 Reset Conversation"):
    st.session_state.cached_result = None
    st.session_state.last_call_time = 0

audio = mic_audio or uploaded_file

# ==================================================
# Processing (Rate-limit safe)
# ==================================================
COOLDOWN_SECONDS = 15

if audio:
    now = time.time()

    if now - st.session_state.last_call_time < COOLDOWN_SECONDS:
        st.warning("⏳ Voice services are under high load. Please retry shortly.")
        st.stop()

    st.session_state.last_call_time = now

    if st.session_state.cached_result:
        user_text, lang, intent, reply, voice_reply = st.session_state.cached_result
    else:
        try:
            with st.spinner("Processing voice input..."):
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(audio.read())
                    audio_path = tmp.name

                user_text = transcribe(audio_path)
                lang = detect(user_text)
                intent = detect_intent(user_text)
                reply = generate_reply(user_text, intent, lang)
                voice_reply = speak(reply, lang)

                st.session_state.cached_result = (
                    user_text, lang, intent, reply, voice_reply
                )

        except Exception:
            st.warning("⚠️ Voice services are temporarily busy. Please try again shortly.")
            st.stop()

    # ==================================================
    # Output
    # ==================================================
    st.markdown("### 📝 Transcription")
    st.write(user_text)

    st.markdown("### 🌍 Detected Language")
    st.write(lang)

    st.markdown("### 🧠 Detected Intent")
    st.markdown(f"<div class='intent-box'>{intent}</div>", unsafe_allow_html=True)

    st.markdown("### 🤖 AI Response")
    st.write(reply)

    st.markdown("### 🔊 Voice Reply")
    st.audio(voice_reply)

# ==================================================
# Footer
# ==================================================
st.divider()
st.markdown("""
<div style="text-align:center;font-size:13px;color:#94a3b8;padding:24px;">
    Made by 
    <a href="https://www.linkedin.com/in/monika-kushwaha-52443735/"
       target="_blank"
       style="color:#60a5fa;text-decoration:none;font-weight:500;">
       Monika Kushwaha
    </a>
    <br/>
    <span style="font-size:12px;color:#64748b;">
        Built for BFSI Voice AI
    </span>
</div>
""", unsafe_allow_html=True)
