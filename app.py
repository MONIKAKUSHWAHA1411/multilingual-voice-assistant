import streamlit as st
import tempfile
import os
from langdetect import detect
import google.generativeai as genai
import whisper
from gtts import gTTS

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="BFSI Multilingual Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# --------------------------------------------------
# Secrets & API Setup
# --------------------------------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# --------------------------------------------------
# UI Styling (Oriserve-style)
# --------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #0b1220;
}
.header-box {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    padding: 28px;
    border-radius: 14px;
    text-align: center;
    color: white;
    margin-bottom: 30px;
}
.subtext {
    color: #dbeafe;
    font-size: 14px;
    margin-top: 6px;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 30px;
}
.small-note {
    font-size: 13px;
    color: #94a3b8;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown("""
<div class="header-box">
    <h2>🎙️ BFSI Multilingual Voice Assistant</h2>
    <div class="subtext">
        Purpose-built Voice AI for Banking & Financial Services
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Load Whisper (cached)
# --------------------------------------------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_model = load_whisper()

# --------------------------------------------------
# BFSI Intent Taxonomy (20+)
# --------------------------------------------------
BFSI_INTENTS = [
    "Account Balance",
    "Mini Statement",
    "Transaction History",
    "Debit Card Block",
    "Credit Card Block",
    "Card Replacement",
    "UPI Issue",
    "ATM Issue",
    "Loan EMI Query",
    "Loan Foreclosure",
    "Interest Rate Query",
    "KYC Update",
    "Address Change",
    "Mobile Number Update",
    "Net Banking Issue",
    "Forgot Password",
    "Fraud Report",
    "Dispute Transaction",
    "Cheque Book Request",
    "Account Closure",
    "General Banking Query",
    "Other"
]

# --------------------------------------------------
# Gemini Intent + Response
# --------------------------------------------------
def gemini_bfsi_response(user_text):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are a BFSI virtual assistant for Indian banking customers.

TASKS:
1. Identify the most relevant intent from this list:
{BFSI_INTENTS}

2. Respond in a polite, professional BFSI tone.
3. Keep response concise and safe (no PII assumptions).

USER QUERY:
\"\"\"{user_text}\"\"\"

OUTPUT FORMAT:
Intent:
Response:
"""

    result = model.generate_content(prompt)
    return result.text

# --------------------------------------------------
# Text-to-Speech (Free)
# --------------------------------------------------
def speak(text, lang):
    tts = gTTS(text=text, lang=lang)
    audio_path = tempfile.mktemp(suffix=".mp3")
    tts.save(audio_path)
    return audio_path

# --------------------------------------------------
# Input Options
# --------------------------------------------------
st.markdown("<div class='section-title'>🎧 Input Options</div>", unsafe_allow_html=True)

input_mode = st.radio(
    "Choose input type:",
    ["Upload recorded call (WAV / MP3)", "Type text message"],
    horizontal=True
)

user_text = None

# --------------------------------------------------
# Option 1: Upload Audio
# --------------------------------------------------
if input_mode == "Upload recorded call (WAV / MP3)":
    audio_file = st.file_uploader(
        "Upload customer call recording",
        type=["wav", "mp3"]
    )

    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_file.read())
            audio_path = tmp.name

        with st.spinner("Transcribing audio..."):
            result = whisper_model.transcribe(audio_path)
            user_text = result["text"]

        st.subheader("📝 Transcription")
        st.write(user_text)

# --------------------------------------------------
# Option 2: Text Input
# --------------------------------------------------
else:
    user_text = st.text_area(
        "Enter customer query",
        placeholder="Eg: Mere savings account mein kitna balance hai?"
    )

# --------------------------------------------------
# Processing
# --------------------------------------------------
if user_text:
    try:
        lang = detect(user_text)
    except:
        lang = "en"

    st.subheader("🌐 Detected Language")
    st.write(lang)

    with st.spinner("Understanding intent & generating response..."):
        output = gemini_bfsi_response(user_text)

    # Parse output
    intent = "Unknown"
    response = output

    if "Intent:" in output and "Response:" in output:
        intent = output.split("Intent:")[1].split("Response:")[0].strip()
        response = output.split("Response:")[1].strip()

    st.subheader("🧠 Detected Intent")
    st.write(intent)

    st.subheader("💬 Assistant Response")
    st.write(response)

    # Voice reply
    try:
        voice_path = speak(response, "hi" if lang == "hi" else "en")
        st.audio(voice_path)
    except:
        st.warning("Voice reply unavailable for this language.")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.markdown("""
<div style="text-align:center; font-size:13px; color:#94a3b8; padding:20px 0;">
    Built for <b>BFSI Voice AI</b><br/>
    Made by 
    <a href="https://www.linkedin.com/in/monika-kushwaha-52443735/"
       target="_blank"
       style="color:#60a5fa; text-decoration:none; font-weight:500;">
       Monika Kushwaha
    </a>
</div>
""", unsafe_allow_html=True)
