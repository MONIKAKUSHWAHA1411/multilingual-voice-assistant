import streamlit as st
import whisper
import tempfile
import os

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Multilingual Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# -----------------------------
# Title & description
# -----------------------------
st.title("🎙 Multilingual Voice Assistant")
st.write("Upload an audio file (English / Hindi / Hinglish)")

# -----------------------------
# Intent detection logic
# -----------------------------
def detect_intent(text: str) -> str:
    text = text.lower()

    if "balance" in text:
        return "Balance Check"
    elif "transaction" in text or "kal" in text or "last" in text:
        return "Last Transaction"
    elif "block" in text or "card" in text:
        return "Card Block"
    else:
        return "General Query"

# -----------------------------
# File upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload audio file",
    type=["wav", "mp3"]
)

# -----------------------------
# Processing
# -----------------------------
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        audio_path = tmp.name

    st.info("Transcribing audio...")

    # Load Whisper model
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    # Clean up temp file
    os.remove(audio_path)

    # -----------------------------
    # Output
    # -----------------------------
    st.subheader("📝 Transcription")
    st.write(result["text"])

    st.subheader("🌍 Detected Language")
    st.write(result["language"])

    intent = detect_intent(result["text"])

    st.subheader("🧠 Detected Intent")
    st.write(intent)
