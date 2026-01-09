import streamlit as st
import os
import speech_recognition as sr
from tempfile import NamedTemporaryFile
from pydub import AudioSegment
from groq import Groq

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Multilingual AI Assistant",
    page_icon="🌍",
    layout="centered"
)

# -----------------------------
# Oriserve-style blue UI
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1f44, #1e3a8a);
    color: white;
}
h1, h2, h3 {
    color: #e0f2fe;
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
# Groq API Key
# -----------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Groq API key not found. Please add it in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# Voice upload
# -----------------------------
st.subheader("🎙 Upload your voice")

audio_file = st.file_uploader(
    "Upload an audio file (WAV or MP3)",
    type=["wav", "mp3"]
)

# -----------------------------
# Speech to text (English + Hindi fallback)
# -----------------------------
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio, language="en-IN")
    except:
        try:
            return recognizer.recognize_google(audio, language="hi-IN")
        except:
            return ""

# -----------------------------
# Simple language detection
# -----------------------------
def detect_language(text):
    if any(char in text for char in "अआइईउऊएऐओऔ"):
        return "Hindi"
    elif any(word in text.lower() for word in ["hai", "nahi", "kyun", "kya", "ka", "ki"]):
        return "Hinglish"
    else:
        return "English"

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

            if not user_text:
                st.error("Sorry, could not understand the audio.")
            else:
                lang = detect_language(user_text)

                st.success("Speech recognized")
                st.markdown("**You said:**")
                st.write(user_text)
                st.info(f"Detected language: {lang}")

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a multilingual AI assistant for BFSI service operations. "
                                "The user may speak in English, Hindi, or Hinglish. "
                                "Always reply in the SAME language style used by the user. "
                                "If the user mixes languages, reply in Hinglish. "
                                "Be clear, polite, and compliant."
                            )
                        },
                        {
                            "role": "user",
                            "content": user_text
                        }
                    ],
                    temperature=0.3
                )

                answer = completion.choices[0].message.content

                st.subheader("🤖 Assistant Response")
                st.write(answer)

        except Exception as e:
            st.error(f"Error processing audio: {e}")

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div class="footer">
    Built with Streamlit + Groq (LLaMA 3)<br>
    Made by <a href="https://www.linkedin.com/in/monika-kushwaha-52443735/" target="_blank">
    Monika Kushwaha
    </a>
</div>
""", unsafe_allow_html=True)
