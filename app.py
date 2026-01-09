import streamlit as st
import whisper
import tempfile
import os
from langdetect import detect
from gtts import gTTS
from openai import OpenAI

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="BFSI Multilingual Voice Assistant",
    layout="centered",
)

# -----------------------------
# Custom Oriserve-style CSS
# -----------------------------
st.markdown("""
<style>
.main {
    background-color:#0b1220;
    color:#e5e7eb;
}
.header {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    padding:24px;
    border-radius:14px;
    text-align:center;
    margin-bottom:30px;
}
.header h1 {
    font-size:28px;
    color:white;
    margin-bottom:6px;
}
.header p {
    color:#dbeafe;
    font-size:14px;
}
.section {
    margin-top:30px;
}
.small {
    font-size:13px;
    color:#94a3b8;
}
.intent-box {
    background:#020617;
    padding:14px;
    border-radius:10px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="header">
    <h1>🎙️ BFSI Multilingual Voice Assistant</h1>
    <p>Purpose-built Voice AI for Banking & Financial Services</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# OpenAI Client
# -----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# Load Whisper Model
# -----------------------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

model = load_whisper()

# -----------------------------
# BFSI Intent Taxonomy (20+)
# -----------------------------
BFSI_INTENTS = {
    "Account Balance Inquiry": ["balance", "kitna paisa", "remaining"],
    "Mini Statement": ["last transactions", "mini statement"],
    "Card Block": ["block card", "card lost", "freeze card"],
    "Card Replacement": ["new card", "replace card"],
    "PIN Generation / Reset": ["reset pin", "forgot pin"],
    "Loan Eligibility": ["loan eligibility", "can I get loan"],
    "Loan EMI Inquiry": ["emi", "monthly installment"],
    "Loan Foreclosure": ["close loan", "foreclosure"],
    "Interest Rate Inquiry": ["interest rate", "roi"],
    "Account Type Conversion": ["salary account", "convert account"],
    "KYC Update": ["update kyc", "kyc pending"],
    "Debit Card Charges": ["card charges", "annual fee"],
    "Credit Card Limit": ["credit limit", "increase limit"],
    "Transaction Failure": ["failed transaction", "money deducted"],
    "UPI Issue": ["upi not working", "upi failed"],
    "Cheque Status": ["cheque status"],
    "Branch Information": ["nearest branch"],
    "Customer Support": ["talk to agent"],
    "Account Closure": ["close account"],
    "Nominee Update": ["add nominee"],
    "Address Update": ["change address"],
}

def detect_intent(text):
    text = text.lower()
    for intent, keywords in BFSI_INTENTS.items():
        if any(k in text for k in keywords):
            return intent
    return "General Banking Query"

# -----------------------------
# LLM Response Generator
# -----------------------------
def llm_reply(text, intent, lang):
    prompt = f"""
You are a BFSI voice assistant.
User language: {lang}
Detected intent: {intent}

Answer politely, clearly, and in a banking-compliant tone.
"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":prompt},
            {"role":"user","content":text}
        ],
        temperature=0.2
    )
    return res.choices[0].message.content

# -----------------------------
# Text-to-Speech
# -----------------------------
def speak(text, lang):
    tts = gTTS(text=text, lang="hi" if lang=="hi" else "en")
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    tts.save(path)
    return path

# -----------------------------
# Input Options
# -----------------------------
st.markdown("## 🎧 Input Options")

audio_input = st.audio_input("🎙️ Speak now")

uploaded_file = st.file_uploader(
    "📁 Upload recorded call (WAV / MP3)",
    type=["wav", "mp3"]
)

audio_file = audio_input or uploaded_file

# -----------------------------
# Processing
# -----------------------------
if audio_file:
    with st.spinner("Transcribing audio..."):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_file.read())
            audio_path = tmp.name

        result = model.transcribe(audio_path)
        text = result["text"]

        lang = detect(text)
        intent = detect_intent(text)

        reply = llm_reply(text, intent, lang)
        voice_path = speak(reply, lang)

    # -----------------------------
    # Output
    # -----------------------------
    st.markdown("### 📝 Transcription")
    st.write(text)

    st.markdown("### 🌍 Detected Language")
    st.write(lang)

    st.markdown("### 🧠 Detected Intent")
    st.markdown(f"<div class='intent-box'>{intent}</div>", unsafe_allow_html=True)

    st.markdown("### 🤖 AI Response")
    st.write(reply)

    st.markdown("### 🔊 Voice Reply")
    st.audio(voice_path)

# -----------------------------
# Footer
# -----------------------------
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
