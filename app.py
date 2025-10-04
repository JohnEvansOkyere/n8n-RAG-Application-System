"""
VexaAI RAG Chat Application - Streamlit UI
"""

import streamlit as st
import requests
import uuid
from datetime import datetime
import time
from typing import List, Dict
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page configuration
st.set_page_config(
    page_title="VexaAI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .timestamp {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1976d2;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
    .sidebar-info {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'chat_history_loaded' not in st.session_state:
        st.session_state.chat_history_loaded = False


def load_chat_history():
    """Load chat history from Supabase"""
    try:
        response = supabase.table('chat_messages')\
            .select('*')\
            .eq('session_id', st.session_state.session_id)\
            .order('created_at', desc=False)\
            .execute()
        
        if response.data:
            st.session_state.messages = [
                {
                    'role': msg['role'],
                    'content': msg['content'],
                    'timestamp': msg['created_at']
                }
                for msg in response.data
            ]
            st.session_state.chat_history_loaded = True
            return True
        return False
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        return False


def send_message(message: str) -> Dict:
    """Send message to n8n webhook"""
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id,
            "user_id": st.session_state.user_id
        }
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. Please try again."
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def get_document_stats():
    """Get document processing statistics"""
    try:
        response = supabase.table('documents')\
            .select('processing_status', count='exact')\
            .execute()
        
        total = len(response.data) if response.data else 0
        
        completed = supabase.table('documents')\
            .select('id', count='exact')\
            .eq('processing_status', 'completed')\
            .execute()
        
        processing = supabase.table('documents')\
            .select('id', count='exact')\
            .eq('processing_status', 'processing')\
            .execute()
        
        failed = supabase.table('documents')\
            .select('id', count='exact')\
            .eq('processing_status', 'failed')\
            .execute()
        
        return {
            'total': total,
            'completed': len(completed.data) if completed.data else 0,
            'processing': len(processing.data) if processing.data else 0,
            'failed': len(failed.data) if failed.data else 0
        }
    except Exception as e:
        st.error(f"Error fetching document stats: {str(e)}")
        return {'total': 0, 'completed': 0, 'processing': 0, 'failed': 0}


def display_message(role: str, content: str, timestamp: str = None):
    """Display a chat message"""
    css_class = "user-message" if role == "user" else "assistant-message"
    icon = "👤" if role == "user" else "🤖"
    
    with st.container():
        st.markdown(f"""
        <div class="chat-message {css_class}">
            <strong>{icon} {role.title()}</strong>
            <p>{content}</p>
            {f'<div class="timestamp">{timestamp}</div>' if timestamp else ''}
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🤖 VexaAI Assistant</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.title("📊 Dashboard")
        
        # Session Information
        with st.expander("📝 Session Info", expanded=True):
            st.markdown(f"""
            <div class="sidebar-info">
                <strong>Session ID:</strong><br/>
                <code>{st.session_state.session_id[:8]}...</code><br/><br/>
                <strong>User ID:</strong><br/>
                <code>{st.session_state.user_id[:8]}...</code>
            </div>
            """, unsafe_allow_html=True)
        
        # Document Statistics
        st.subheader("📄 Knowledge Base")
        stats = get_document_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Docs", stats['total'])
            st.metric("Processing", stats['processing'])
        with col2:
            st.metric("Completed", stats['completed'])
            st.metric("Failed", stats['failed'])
        
        # Actions
        st.markdown("---")
        st.subheader("⚙️ Actions")
        
        if st.button("🔄 Load Chat History"):
            with st.spinner("Loading history..."):
                if load_chat_history():
                    st.success("Chat history loaded!")
                else:
                    st.info("No previous chat history found.")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
        
        if st.button("🔄 New Session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.chat_history_loaded = False
            st.rerun()
        
        # Information
        st.markdown("---")
        with st.expander("ℹ️ About"):
            st.markdown("""
            **VexaAI Assistant** uses RAG (Retrieval Augmented Generation) 
            to answer questions based on the VexaAI FAQ knowledge base.
            
            **Features:**
            - Real-time chat interface
            - Vector-based search
            - Session persistence
            - Document processing pipeline
            """)
    
    # Main chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        if not st.session_state.messages:
            st.info("👋 Welcome! Ask me anything about VexaAI. I'll search the knowledge base to help you.")
        else:
            for message in st.session_state.messages:
                display_message(
                    message['role'],
                    message['content'],
                    message.get('timestamp')
                )
    
    # Chat input
    st.markdown("---")
    
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Your message:",
                placeholder="Type your question here...",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("Send 📤")
    
    # Handle message submission
    if submit_button and user_input:
        # Add user message to chat
        user_message = {
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.messages.append(user_message)
        
        # Display user message immediately
        with chat_container:
            display_message(user_message['role'], user_message['content'])
        
        # Send to n8n and get response
        with st.spinner("🤔 Thinking..."):
            response = send_message(user_input)
        
        if response.get('success'):
            assistant_content = response.get('data', {}).get('message', 'No response received.')
            
            assistant_message = {
                'role': 'assistant',
                'content': assistant_content,
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.messages.append(assistant_message)
            
            # Rerun to display assistant message
            st.rerun()
        else:
            error_message = response.get('error', 'Unknown error occurred.')
            st.error(f"❌ Error: {error_message}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
        "Powered by VexaAI | Built with Streamlit & n8n"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()