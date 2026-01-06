import streamlit as st
import whisper
import tempfile
import os

st.set_page_config(page_title="Multilingual Voice Assistant")

st.title("🎙 Multilingual Voice Assistant")
st.write("Upload an audio file (English / Hindi / Hinglish)")

uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        audio_path = tmp.name

    st.info("Transcribing audio…")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    st.subheader("📝 Transcription")
    st.write(result["text"])

    st.subheader("🌍 Detected Language")
    st.write(result["language"])

    os.remove(audio_path)
