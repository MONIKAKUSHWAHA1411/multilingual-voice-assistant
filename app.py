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

st.title("🌍 Multilingual AI Assistant")
st.caption("AI-powered assistant for multilingual service operations")

# -----------------------------
# API Key
# -----------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google API key not found. Add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# -----------------------------
# Gemini model (WORKING)
# -----------------------------
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# -----------------------------
# Audio upload
# -----------------------------
st.subheader("🎙 Upload your voice")

audio_file = st.file_uploader(
    "Upload an audio file (wav/mp3)",
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
            # Save uploaded file
            with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                audio = AudioSegment.from_file(audio_file)
                audio.export(tmp.name, format="wav")
                audio_path = tmp.name

            # Speech to text
            user_text = speech_to_text(audio_path)

            st.success("Speech recognized")
            st.write("**You said:**")
            st.write(user_text)

            # Gemini response
            response = model.generate_content(
                f"""
You are a helpful AI assistant for service operations.
Respond clearly and politely.
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
st.caption("Built with Streamlit + Google Gemini | Voice-first AI assistant")
