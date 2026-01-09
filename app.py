import streamlit as st
import os
import google.generativeai as genai

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Multilingual AI Assistant",
    page_icon="🌍",
    layout="centered"
)

# -----------------------------
# App title
# -----------------------------
st.title("🌍 Multilingual AI Assistant")
st.caption("AI-powered assistant designed for multilingual service operations")

# -----------------------------
# Load API Key
# -----------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google API key not found. Please add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# -----------------------------
# Model setup (Free & Stable)
# -----------------------------
MODEL_NAME = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# -----------------------------
# Session state
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# Input section
# -----------------------------
st.subheader("💬 Ask something")

user_input = st.text_area(
    "Enter your message (any language)",
    placeholder="Example: Explain AI automation in simple terms",
    height=120
)

# -----------------------------
# Generate response
# -----------------------------
if st.button("Generate Response"):
    if not user_input.strip():
        st.warning("Please enter a message.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = model.generate_content(
                    f"""
You are a helpful AI assistant designed for service operations.
Respond clearly, politely, and concisely.
If the input is not in English, respond in the same language.

User query:
{user_input}
"""
                )

                answer = response.text

                st.session_state.chat_history.append(
                    {"user": user_input, "assistant": answer}
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")

# -----------------------------
# Chat history
# -----------------------------
if st.session_state.chat_history:
    st.subheader("🗂 Conversation")
    for chat in reversed(st.session_state.chat_history):
        st.markdown("**You:**")
        st.write(chat["user"])
        st.markdown("**Assistant:**")
        st.write(chat["assistant"])
        st.divider()

# -----------------------------
# Footer
# -----------------------------
st.caption("Built using Streamlit + Google Gemini | Scalable AI assistant demo")
