import streamlit as st
import whisper
import tempfile
import os

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Multilingual Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# -------------------------------------------------
# Title
# -------------------------------------------------
st.title("🎙 Multilingual Voice Assistant")
st.write("Upload an audio file (English / Hindi / Hinglish)")

# -------------------------------------------------
# Intent Detection (Knowledge-base driven)
# -------------------------------------------------
def detect_intent(text: str) -> str:
    text = text.lower()

    balance_keywords = [
        "balance", "account balance", "kitna paisa", "paise", "amount"
    ]

    transaction_keywords = [
        "transaction", "last transaction", "debit", "credit", "spent", "kal"
    ]

    card_block_keywords = [
        "block card", "card block", "lost card", "stolen card", "freeze card"
    ]

    account_conversion_keywords = [
        "salary account",
        "savings account",
        "convert",
        "change account",
        "account type",
        "upgrade account"
    ]

    card_eligibility_keywords = [
        "new card",
        "apply for card",
        "card converted",
        "replace card",
        "existing card",
        "card validity"
    ]

    fees_keywords = [
        "charges", "fees", "minimum balance", "penalty"
    ]

    # Order matters – higher intent first
    if any(word in text for word in account_conversion_keywords):
        return "Account Conversion / Account Type Change"

    elif any(word in text for word in card_eligibility_keywords):
        return "Card Eligibility / Replacement"

    elif any(word in text for word in card_block_keywords):
        return "Card Block / Lost Card"

    elif any(word in text for word in transaction_keywords):
        return "Transaction History"

    elif any(word in text for word in balance_keywords):
        return "Account Balance"

    elif any(word in text for word in fees_keywords):
        return "Fees & Charges"

    else:
        return "General Banking Query"

# -------------------------------------------------
# Suggested BFSI-style response
# -------------------------------------------------
def suggested_response(intent: str) -> str:
    responses = {
        "Account Conversion / Account Type Change":
            "Account conversion depends on eligibility and employer documentation. In most cases, existing debit cards continue to work, but some banks may issue a new card. Please check with customer support for exact policy.",

        "Card Eligibility / Replacement":
            "Card eligibility depends on your account type and usage. You may apply for a new card via net banking, mobile app, or by visiting a branch.",

        "Card Block / Lost Card":
            "Please block your card immediately using mobile banking or customer support to prevent unauthorized transactions.",

        "Transaction History":
            "You can view your recent transactions through mobile banking, net banking, or by requesting a mini statement.",

        "Account Balance":
            "You can check your account balance using mobile banking, SMS banking, ATM, or net banking services.",

        "Fees & Charges":
            "Charges vary by account type. Please refer to the bank’s official schedule of charges or contact support."
    }

    return responses.get(
        intent,
        "Please contact customer support for detailed assistance regarding your query."
    )

# -------------------------------------------------
# File Upload
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload audio file",
    type=["wav", "mp3"]
)

# -------------------------------------------------
# Processing
# -------------------------------------------------
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        audio_path = tmp.name

    st.info("Transcribing audio...")

    # Load Whisper model
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    os.remove(audio_path)

    # -------------------------------------------------
    # Output
    # -------------------------------------------------
    st.subheader("📝 Transcription")
    st.write(result["text"])

    st.subheader("🌍 Detected Language")
    st.write(result["language"])

    intent = detect_intent(result["text"])

    st.subheader("🧠 Detected Intent")
    st.write(intent)

    st.subheader("💡 Suggested Response")
    st.write(suggested_response(intent))
