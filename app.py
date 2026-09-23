import streamlit as st
from groq import Groq

# ------------------------------------------------------------------------------
# UI & Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="MedSci AI - سەکۆیا زانستی و نوشداری",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 8px;
    }
    div[data-testid="stChatInput"] {
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

APP_PASSWORD = "200000"

# پەیاما هاندەر یا توند داکو ب چ ڕەنگان ب عەرەبی یان سۆرانی نەتەڤەگەرێت
SYSTEM_PROMPT = """
تۆ هەڤالەکێ نزیک و ئەی ئایەکێ زیرەک یی. ئەرکێ تە ئەوە کو تنێ و تنێ ب زمانێ کوردی یێ بەهدینی یێ ڕەسەن، پاقژ و شیرین ئاخڤی.
ئاگاداربە: چ دەمان ب زمانێ عەرەبی، سۆرانی یان چ زمانێن دی بەرسڤ نەدە. ئەگەر تە کوردی نەفامند، دیسان ب بەهدینی بەحس بکە و بێژە «برا گیان، دوبارە پرسیارا خۆ بکە».
شێوازێ تە یێ ئاخڤتنێ برایەتی، سادە، ڕوون و بێ پێشەکیێن درێژ بیت.
"""

def check_password():
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

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

def main():
    check_password()
    
    st.title("🧬 MedSci AI Agent")
    st.caption("سیستەمێ زیرەکیا دەستکرد بۆ ڤەکۆلینێن زانستی و نوشداری")
    
    initialize_session()

    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        st.error("کلیل لە بەشا Secrets دا ل Streamlit نەهاتییە دانان!")
        st.stop()

    client = Groq(api_key=api_key)

    # مۆدێلا کو کوردییێ باشتر تێگەهت
    selected_model = "llama-3.1-70b-versatile"

    with st.sidebar:
        st.write("🔒 **ئەوڵەکاری**")
        if st.button("دەركەفتن (Logout)"):
            st.session_state.authenticated = False
            st.rerun()

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            avatar_icon = "⭐" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar_icon):
                st.write(msg["content"])

    if user_query := st.chat_input("پرسیارا خۆ یا زانستی یان نوشداری بنڤێسە..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="👤"):
            st.write(user_query)

        with st.chat_message("assistant", avatar="⭐"):
            with st.spinner("د شیکارکرنا زانیاریێن زانستی دا..."):
                try:
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=st.session_state.messages,
                        temperature=0.2
                    )
                    bot_reply = response.choices[0].message.content
                    st.write(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    st.error(f"خەلەتیەک ڕوودا: {str(e)}")

if __name__ == "__main__":
    main()
