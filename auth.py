"""
Authentication System for VexaAI
"""

import streamlit as st
import hashlib
import uuid
from datetime import datetime
from supabase import Client


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def create_user(supabase: Client, username: str, email: str, password: str):
    """Create a new user"""
    try:
        # Check if username or email already exists
        existing = supabase.table('users')\
            .select('*')\
            .or_(f'username.eq.{username},email.eq.{email}')\
            .execute()
        
        if existing.data:
            return {
                'success': False,
                'error': 'Username or email already exists'
            }
        
        # Create user
        user_data = {
            'id': str(uuid.uuid4()),
            'username': username,
            'email': email,
            'password_hash': hash_password(password),
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        return {
            'success': True,
            'user': result.data[0]
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def login_user(supabase: Client, username: str, password: str):
    """Login user"""
    try:
        # Get user by username
        result = supabase.table('users')\
            .select('*')\
            .eq('username', username)\
            .execute()
        
        if not result.data:
            return {
                'success': False,
                'error': 'Invalid username or password'
            }
        
        user = result.data[0]
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return {
                'success': False,
                'error': 'Invalid username or password'
            }
        
        # Update last login
        supabase.table('users')\
            .update({'updated_at': datetime.now().isoformat()})\
            .eq('id', user['id'])\
            .execute()
        
        return {
            'success': True,
            'user': user
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def logout_user():
    """Logout user"""
    keys_to_clear = ['authenticated', 'user_id', 'username', 'email']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def show_login_page(supabase: Client):
    """Display login/signup page with modern UI"""
    
    st.markdown("""
    <style>
        .auth-container {
            max-width: 450px;
            margin: 4rem auto;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        }
        
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .auth-logo {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        .auth-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .auth-subtitle {
            color: #6b7280;
            font-size: 1rem;
        }
        
        .auth-tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e5e7eb;
        }
        
        .auth-tab {
            flex: 1;
            padding: 1rem;
            text-align: center;
            cursor: pointer;
            font-weight: 600;
            color: #6b7280;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .auth-tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .divider {
            text-align: center;
            margin: 2rem 0;
            position: relative;
        }
        
        .divider::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            width: 100%;
            height: 1px;
            background: #e5e7eb;
        }
        
        .divider span {
            background: white;
            padding: 0 1rem;
            position: relative;
            color: #6b7280;
            font-size: 0.875rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <div class="auth-logo">🤖</div>
            <h1 class="auth-title">VexaAI Assistant</h1>
            <p class="auth-subtitle">Sign in to continue your conversation</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab selection
    tab = st.radio(
        "Select",
        ["Login", "Sign Up"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if tab == "Login":
        show_login_form(supabase)
    else:
        show_signup_form(supabase)
    
    # Footer
    st.markdown("""
    <div style='text-align: center; margin-top: 3rem; color: #6b7280; font-size: 0.875rem;'>
        🔒 Your data is secure and encrypted
    </div>
    """, unsafe_allow_html=True)


def show_login_form(supabase: Client):
    """Display login form"""
    with st.form("login_form", clear_on_submit=False):
        st.markdown("### 🔐 Login")
        
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            remember = st.checkbox("Remember me", value=True)
        
        submit = st.form_submit_button("Login 🚀", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("❌ Please enter both username and password")
                return
            
            with st.spinner("Logging in..."):
                result = login_user(supabase, username, password)
            
            if result['success']:
                user = result['user']
                st.session_state.authenticated = True
                st.session_state.user_id = user['id']
                st.session_state.username = user['username']
                st.session_state.email = user['email']
                st.success(f"✅ Welcome back, {user['username']}!")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ {result['error']}")


def show_signup_form(supabase: Client):
    """Display signup form"""
    with st.form("signup_form", clear_on_submit=True):
        st.markdown("### ✨ Create Account")
        
        username = st.text_input(
            "Username",
            placeholder="Choose a username",
            key="signup_username"
        )
        
        email = st.text_input(
            "Email",
            placeholder="your.email@example.com",
            key="signup_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Choose a strong password",
            key="signup_password"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password",
            key="signup_confirm"
        )
        
        agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submit = st.form_submit_button("Create Account ✨", use_container_width=True)
        
        if submit:
            # Validation
            if not username or not email or not password or not confirm_password:
                st.error("❌ Please fill in all fields")
                return
            
            if len(username) < 3:
                st.error("❌ Username must be at least 3 characters")
                return
            
            if len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
                return
            
            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return
            
            if not agree:
                st.error("❌ Please agree to the Terms of Service")
                return
            
            if '@' not in email:
                st.error("❌ Please enter a valid email address")
                return
            
            with st.spinner("Creating your account..."):
                result = create_user(supabase, username, email, password)
            
            if result['success']:
                st.success("✅ Account created successfully! Please login.")
                st.balloons()
            else:
                st.error(f"❌ {result['error']}")


def require_authentication(supabase: Client):
    """Check if user is authenticated, show login if not"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page(supabase)
        return False
    
    return True


def show_user_profile():
    """Display user profile in sidebar"""
    if st.session_state.get('authenticated'):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Profile")
        
        st.sidebar.markdown(f"""
        <div class="sidebar-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="width: 60px; height: 60px; border-radius: 50%; 
                     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                     margin: 0 auto; display: flex; align-items: center; 
                     justify-content: center; font-size: 1.5rem; color: white;">
                    {st.session_state.username[0].upper()}
                </div>
            </div>
            <div style="text-align: center;">
                <strong>{st.session_state.username}</strong><br>
                <small style="color: #6b7280;">{st.session_state.email}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.success("✅ Logged out successfully!")
            st.rerun()