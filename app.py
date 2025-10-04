"""
VexaAI RAG Chat Application - Real World Professional UI
"""

import streamlit as st
import requests
import uuid
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from auth import require_authentication, show_user_profile

# Load environment variables
load_dotenv()

# Config
WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit page
st.set_page_config(page_title="VexaAI Assistant", page_icon="🤖", layout="wide")

# ----------------------------
# CSS Styling
# ----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu, header, footer {visibility: hidden;}

    body { background: #0f172a; color: #f8fafc; }

    .main-header {
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: rgba(255,255,255,0.04);
        border-radius: 14px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #38bdf8;
        margin: 0;
    }
    .main-header p { color: #94a3b8; margin: 0.4rem 0 0; }

    /* Chat container */
    .chat-container {
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 1rem;
        height: 65vh;
        overflow-y: auto;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 0.9rem 1.2rem;
        border-radius: 14px;
        margin-bottom: 0.8rem;
        max-width: 75%;
        line-height: 1.5;
    }
    .user-message {
        background: linear-gradient(135deg, #2563eb, #1e40af);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    .assistant-message {
        background: linear-gradient(135deg, #10b981, #047857);
        color: white;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    .timestamp {
        font-size: 0.7rem;
        color: #cbd5e1;
        margin-top: 0.3rem;
        text-align: right;
    }

    /* Input */
    .input-container {
        background: rgba(15,23,42,0.9);
        padding: 0.8rem;
        border-radius: 12px;
        box-shadow: 0 -2px 12px rgba(0,0,0,0.2);
    }
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #334155;
        padding: 0.7rem 1rem;
        font-size: 0.95rem;
        color: #f1f5f9;
        background: #1e293b;
    }
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(135deg, #38bdf8, #0ea5e9);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1rem;
    }
    [data-testid="stSidebar"] { background: #1e293b; color: #f1f5f9; }
    .sidebar-card {
        background: #0f172a;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Core Logic
# ----------------------------
def initialize_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_message(role: str, content: str, timestamp: str = None):
    css_class = "user-message" if role == "user" else "assistant-message"
    time_str = ""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            time_str = dt.strftime("%I:%M %p")
        except:
            time_str = ""
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <div>{content}</div>
        {f'<div class="timestamp">{time_str}</div>' if time_str else ''}
    </div>
    """, unsafe_allow_html=True)

def send_message(message: str):
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id,
            "user_id": st.session_state.user_id
        }
        response = requests.post(WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

# ----------------------------
# Main
# ----------------------------
def main():
    if not require_authentication(supabase):
        return

    initialize_session_state()

    # Header
    st.markdown('<div class="main-header"><h1>🤖 VexaAI Assistant</h1><p>Your team\'s knowledge — available by chat. (Docs from Google Drive)</p></div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        show_user_profile()
        st.markdown("### 📊 Knowledge Base")
        stats = {"total": 25, "completed": 22, "processing": 2, "failed": 1}
        st.metric("📚 Total", stats["total"])
        st.metric("✅ Ready", stats["completed"])
        st.metric("⏳ Processing", stats["processing"])
        st.metric("❌ Failed", stats["failed"])
        st.markdown("---")
        st.markdown("### ⚙️ Chat Controls")
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.success("✅ Started a new session")
            time.sleep(0.5)
            st.rerun()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.success("✅ Chat cleared")
            time.sleep(0.5)
            st.rerun()

    # Chat area
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.info("👋 Welcome! Start chatting with VexaAI.")
    else:
        for msg in st.session_state.messages:
            display_message(msg["role"], msg["content"], msg.get("timestamp"))
    st.markdown('</div>', unsafe_allow_html=True)

    # Input
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6,1])
        with col1:
            user_input = st.text_input("Message", placeholder="Ask something... 💬", label_visibility="collapsed")
        with col2:
            submit = st.form_submit_button("Send 📤", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if submit and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": datetime.now().isoformat()})
        with st.spinner("🤔 Thinking..."):
            resp = send_message(user_input)
        if resp.get("success"):
            st.session_state.messages.append({"role": "assistant", "content": resp["data"]["message"], "timestamp": datetime.now().isoformat()})
            st.rerun()
        else:
            st.error(f"❌ {resp.get('error')}")

    # Footer
    st.markdown("<div style='text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:1rem;'>✨ Powered by VexaAI | Built with ❤️ using Streamlit & n8n</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
