import streamlit as st
import os
import google.generativeai as genai
import speech_recognition as sr
from tempfile import NamedTemporaryFile
from pydub import AudioSegment

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Multilingual AI Assistant",
    page_icon="🌍",
    layout="centered"
)

# -----------------------------
# Custom CSS (Oriserve blue vibe)
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e3a8a);
    color: white;
}
h1, h2, h3, h4 {
    color: #e0f2fe;
}
.stFileUploader label {
    color: #e0f2fe !important;
}
.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
}
.stButton button:hover {
    background-color: #1d4ed8;
}
.footer {
    text-align: center;
    margin-top: 40px;
    color: #c7d2fe;
}
.footer a {
    color: #93c5fd;
    text-decoration: none;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.title("🌍 Multilingual AI Assistant")
st.caption("AI-powered assistant for multilingual service operations (BFSI-ready)")

# -----------------------------
# API Key
# -----------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google API key not found. Please add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# -----------------------------
# ✅ WORKING Gemini model
# -----------------------------
model = genai.GenerativeModel("models/gemini-pro")

# -----------------------------
# Voice upload
# -----------------------------
st.subheader("🎙 Upload your voice")
audio_file = st.file_uploader(
    "Upload an audio file (WAV or MP3)",
    type=["wav", "mp3"]
)

def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio)

# -----------------------------
# Process audio
# -----------------------------
if audio_file:
    with st.spinner("Processing audio..."):
        try:
            with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                audio = AudioSegment.from_file(audio_file)
                audio.export(tmp.name, format="wav")
                audio_path = tmp.name

            user_text = speech_to_text(audio_path)

            st.success("Speech recognized")
            st.markdown("**You said:**")
            st.write(user_text)

            response = model.generate_content(
                f"""
You are a professional AI voice assistant designed for BFSI service operations.
Respond clearly, politely, and in a compliant tone.
If the user speaks in a non-English language, reply in the same language.

User query:
{user_text}
"""
            )

            st.subheader("🤖 Assistant Response")
            st.write(response.text)

        except Exception as e:
            st.error(f"Error processing audio: {e}")

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div class="footer">
    Built with Streamlit + Google Gemini<br>
    Made by <a href="https://www.linkedin.com/in/monika-kushwaha-52443735/" target="_blank">
    Monika Kushwaha
    </a>
</div>
""", unsafe_allow_html=True)
