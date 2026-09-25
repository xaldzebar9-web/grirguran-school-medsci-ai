import streamlit as st
import google.generativeai as genai

# ------------------------------------------------------------------------------
# UI & Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="ئامادەیا گرگوران - MedSci AI",
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

# پەیاما هاندەر ب بەهدینییەکا پاقژ، نەرم و برایەتی
SYSTEM_PROMPT = """
تۆ هەڤالەکێ نزیک و ئەی ئایەکێ زیرەک یی د بوارێ زانست و نوشداری دا. 
مەرجێن سەرەکی بۆ بەرسڤێن تە:
1. هەمیشە تنێ ب زمانێ کوردی یێ بەهدینی یێ پاقژ، شیرین و سادە ئاخڤە (چ دەمێ سۆرانی یان زمانێن دی بکار نەئینە).
2. شێوازێ ئاخڤتنا تە وەکێ برا و هەڤالەکی بێ؛ دوور بە ژ پێشەکیێن درێژ، گرێدایی یان ئەکادیمیێن توند. ڕاستەوخۆ بچە سەر مەرەمێ.
3. بەرسڤێن تە باوەرپێکری، ڕوون، ب کورتی و ب شێوازەکێ چاتی یێ نەرم و جوان بن.
4. ئەگەر پرسیار لە سەر تشتێن تەندروستی یان نوژداری بوو، زانیاریێن پێدڤی بدە، لێ بێخە بیرا بکارئینەری کو ئەڤە تنێ بۆ زانین و ڤەکۆلینێ یە.
"""

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 چوونە ژوور ب پاسۆردێ")
        st.caption("ژ بۆ بکارئینانا سیستەمی، تکایە پاسۆردێ بنڤێسە.")
        
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
        st.session_state.messages = []

def main():
    check_password()

    # دانانا لوگویا قوتابخانێ ب ڕێکا HTML یا ڕاستەوخۆ (بێ کێشە و خەلەتی)
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <img src="https://raw.githubusercontent.com/xaldzebar9-web/grirguran-school-medsci-ai/main/logo.png.jpg" width="160" style="border-radius: 10px;">
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<h4 style='text-align: center;'>ئامادەیا گرگوران یا تێکەڵ</h4>", unsafe_allow_html=True)
        st.divider()
        
        st.write("🔒 **ئەوڵەکاری**")
        if st.button("دەركەفتن (Logout)"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.title("🧬 MedSci AI Agent")
    st.caption("سیستەمێ زیرەکیا دەستکرد بۆ ڤەکۆلینێن زانستی و نوشداری")
    
    initialize_session()

    # وەرگرتنا کلیلا Gemini ب شێوازەکێ ئەمین ژ بەشا Secrets
    if "GEMINI_API_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_API_KEY"]
    else:
        st.error("کلیلا GEMINI_API_KEY لە بەشا Secrets دا ل Streamlit نەهاتییە دانان!")
        st.stop()

    genai.configure(api_key=gemini_key)
    
    generation_config = {
        "temperature": 0.3,
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT
    )

    # نیشاندانا مێژووا چاتێ
    for message in st.session_state.messages:
        avatar_icon = "⭐" if message["role"] == "model" else "👤"
        role_to_show = "assistant" if message["role"] == "model" else "user"
        with st.chat_message(role_to_show, avatar=avatar_icon):
            st.write(message["parts"][0])

    if user_query := st.chat_input("پرسیارا خۆ یا زانستی یان نوشداری بنڤێسە..."):
        st.session_state.messages.append({"role": "user", "parts": [user_query]})
        with st.chat_message("user", avatar="👤"):
            st.write(user_query)

        with st.chat_message("assistant", avatar="⭐"):
            with st.spinner("د شیکارکرنا زانیاریێن زانستی دا..."):
                try:
                    chat = model.start_chat(history=st.session_state.messages[:-1])
                    response = chat.send_message(user_query)
                    bot_reply = response.text
                    
                    st.write(bot_reply)
                    st.session_state.messages.append({"role": "model", "parts": [bot_reply]})
                except Exception as e:
                    st.error(f"خەلەتیەک ڕوودا: {str(e)}")

if __name__ == "__main__":
    main()
