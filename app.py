import streamlit as st
from openai import OpenAI

# ==============================================================================
# Application Configuration & UI Setup
# ==============================================================================
st.set_page_config(
    page_title="MedSci AI - سەکۆیا زانستی و نوشداری",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI polish
st.markdown("""
    <style>
    .stChatMessage { font-size: 16px; }
    .stTextInput > div > div > input { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# Constants & Security Setup
# ==============================================================================
DEFAULT_MODEL = "gpt-4o"
APP_PASSWORD = "200000"

SYSTEM_PROMPT = """
تۆ ئەی ئایەکێ زۆرا پێشکەفتی یی د بوارێ زانست، نوشداری، و نیشتەگەریێ دا (Medical & Surgical Sciences).
ئەرکێ تە ئەڤەیە:
1. بەرسڤێن تە ب هووربینیەکا زانستی یا بڵند بن د بوارێن ئاناتۆمی، فارماکۆلۆجی، جڕاحی، و زانستێن گشتی دا.
2. تەنی ب شێوازەکێ ڕوون و ئەکادیمی بەرسڤا پرسیاران بدە.
3. ئەگەر پرسیار ل سەر ڕێکارێن نیشتەگەریێ یان تەندروستیێ بوو، زانیاریێن گشتگیر ب دە ئەنجامدان، بەلێ هەمودەم ببیرا بکارئینەری بینە کو ئەڤ ئامرازە بوو مەبەستا فێرکاری و ڤەکۆلینێ یە.
"""

# ==============================================================================
# Authentication Check Function
# ==============================================================================
def check_password():
    """Returns True if the user enters the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 چوونە ژوور ب پاسۆردێ")
        st.caption("ژ بۆ بکارئینانا MedSci AI، تکایە پاسۆردێ بنڤێسە.")
        
        pwd_input = st.text_input("پاسۆرد (Password):", type="password")
        if st.button("چوونە ژوور"):
            if pwd_input == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("پاسۆرد شاشە! تکایە دووبارە تاقیبکەوە.")
        st.stop()

# ==============================================================================
# Helper Functions
# ==============================================================================
def initialize_session():
    """Initializes chat history in Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

# ==============================================================================
# Main Application Core
# ==============================================================================
def main():
    # Verify password before loading main features
    check_password()
    
    st.title("🧬 MedSci AI Agent")
    st.caption("سیستەمێ زیرەکیا دەستکرد بوو ڤەکۆلینێن زانستی و نوشداری")
    
    initialize_session()

    # Read API Key safely from Secrets
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        st.error("کلیل د بەشا Secrets دا ل Streamlit نەهاتییە دانان!")
        st.stop()

    client = OpenAI(api_key=api_key)

    # Logout button in sidebar
    with st.sidebar:
        st.write("🔒 **ئەوڵەکاری**")
        if st.button("دەركەفتن (Logout)"):
            st.session_state.authenticated = False
            st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # User input
    if user_query := st.chat_input("پرسیارا خو بکە..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            with st.spinner("د شیکارکرنا زانیاریێن زانستی دا..."):
                try:
                    response = client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=st.session_state.messages,
                        temperature=0.3
                    )
                    bot_reply = response.choices[0].message.content
                    st.write(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    st.error(f"خەلەتیەک ڕوودا: {str(e)}")

if __name__ == "__main__":
    main()
