# 🌍 Multilingual AI Assistant (Voice-first, BFSI-ready)

A **voice-first multilingual AI assistant** built to demonstrate how modern LLMs can power **BFSI service operations** like collections, renewals, and customer support — with strong support for **English, Hindi, and Hinglish**.

This project is designed as a **production-safe POC** aligned with Oriserve / ORI-style voice bots.

---

## ✨ What this project shows

* 🎙 **Voice-first UX** (audio upload → speech → AI response)
* 🌐 **Multilingual handling**: English, Hindi, Hinglish
* 🧠 **Fast LLM inference** using Groq (LLaMA 3)
* 🏦 **BFSI-compliant tone** baked into prompts
* ⚡ **Low-latency responses** suitable for real-time voice bots
* 🎨 **Enterprise blue UI** inspired by Oriserve branding

---

## 🧠 Architecture

```
User Voice (WAV / MP3)
        ↓
Speech Recognition (Google STT)
        ↓
Language Detection (English / Hindi / Hinglish)
        ↓
Groq LLM (LLaMA 3.1)
        ↓
Text Response (same language style)
```

---

## 🛠 Tech Stack

* **Frontend**: Streamlit
* **Speech-to-Text**: SpeechRecognition (Google backend)
* **LLM**: Groq (LLaMA 3.1 – 8B Instant)
* **Audio Processing**: pydub
* **Deployment**: Streamlit Cloud

---

## 🌐 Language Support

The assistant automatically adapts to how the user speaks:

| User Speech | Assistant Response |
| ----------- | ------------------ |
| English     | English            |
| Hindi       | Hindi              |
| Hinglish    | Hinglish           |

This mirrors **real Indian BFSI customer conversations**, especially in collections and support calls.

---

## 🚀 How to Run Locally

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd multilingual-ai-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variable

```bash
export GROQ_API_KEY="your_groq_api_key"
```

(or add it in Streamlit Secrets)

### 4. Run the app

```bash
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Push code to GitHub
2. Create a Streamlit Cloud app
3. Add secret:

```toml
GROQ_API_KEY="your_groq_api_key"
```

4. Reboot app

---

## 🎯 Why Groq + LLaMA 3?

* Extremely **low latency** (ideal for voice bots)
* **Stable SDK** on Streamlit Cloud
* Open-weight LLMs → vendor flexibility
* Great multilingual performance

For POCs and demos, **reliability > experimental features**.

---

## 🏦 BFSI Use Cases

* Loan collections voice assistant
* Card blocking / account queries
* Renewal & follow-up calls
* Multilingual customer support

---

## 🔮 Possible Extensions

* 🔊 Text-to-Speech (Hindi + English)
* 🎯 Intent classification (Collection / Renewal / Support)
* 📊 Confidence scoring
* 🧾 Conversation logging for audits

---

## 👩‍💻 Author

**Made by Monika Kushwaha**
🔗 LinkedIn: [https://www.linkedin.com/in/monika-kushwaha-52443735/](https://www.linkedin.com/in/monika-kushwaha-52443735/)

---

## 📌 Note

This project is a **functional POC**, not a production system. It is intentionally designed to demonstrate **architecture, UX decisions, and AI integration strategy** relevant to BFSI voice automation platforms like Oriserve / ORI.
