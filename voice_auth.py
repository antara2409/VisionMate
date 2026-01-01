# voice_auth.py

import streamlit as st
import re
import time
import database as db # Assumed to be your existing database module
from audio_utils import play_audio, listen_for_voice, match_command

# --- Helper Validation Functions ---

def validate_name(name):
    return bool(re.match(r"^[A-Za-z ]{2,}$", name.strip()))

def validate_email(email):
    return bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email))

def validate_password(password):
    if len(password) < 6: return False
    lowered = password.lower()
    return lowered not in ["password", "123456", "qwerty", "test123", "admin", "letmein"]

# ==================== WELCOME STATE ====================
def welcome_state():
    st.markdown('<div class="title-box">VisionMate</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan-box">Navigate with clarity, live with freedom.</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-box">Secure and automatic voice-based authentication system.</div>', unsafe_allow_html=True)
    st.markdown('<div class="instruction-box">Say "Register" to create account<br>Say "Login" to sign in</div>', unsafe_allow_html=True)

    # Always play audio when entering welcome state
    play_audio("Welcome to Visionmate. Navigate with clarity, live with freedom. Say Register to create a new account, or Login to sign in for secure, hands-free authentication.")
    
    # Listen for voice command
    cmd = listen_for_voice(wait_before_listen=4)
    
    if cmd:
        cmd = cmd.lower()
        if match_command(cmd, ["register", "registration", "sign up", "signup"]):
            play_audio("Starting registration process.")
            st.session_state.state = "reg_name"
            st.session_state.tmp = {}
            time.sleep(2)
            st.rerun()
        elif match_command(cmd, ["login", "sign in", "signin"]):
            play_audio("Starting login process.")
            st.session_state.state = "login_user"
            st.session_state.tmp = {}
            time.sleep(2)
            st.rerun()
        else:
            play_audio("Sorry, I couldn't understand. Please say Register or Login clearly.")
            time.sleep(2)
            st.rerun()
    else:
        play_audio("No command received. Please try again.")
        time.sleep(2)
        st.rerun()

# ==================== REGISTRATION STATES ====================
def reg_name_state():
    st.markdown('<div class="title-box">Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-indicator">Step 1 of 4: Name</div>', unsafe_allow_html=True)
    st.markdown('<div class="instruction-box">Say your full name.</div>', unsafe_allow_html=True)
    play_audio("Step one of four. Say your full name after the countdown.")
    
    name = listen_for_voice(wait_before_listen=3)
    
    if name:
        name_lower = name.lower()
        if match_command(name_lower, ["cancel", "back", "stop"]):
            play_audio("Cancelling registration. Returning to main menu.")
            st.session_state.state = "welcome"
            time.sleep(2)
            st.rerun()
        elif not validate_name(name):
            st.markdown('<div class="error-box">Invalid name. Use letters and spaces only.</div>', unsafe_allow_html=True)
            play_audio("Invalid name. Name must contain only letters and spaces, at least two characters. Please try again.")
            time.sleep(3)
            st.rerun()
        else:
            st.session_state.tmp["name"] = name
            st.markdown(f'<div class="success-box">Name: {name.title()}</div>', unsafe_allow_html=True)
            play_audio(f"Thank you. Your name {name} is saved. Proceeding to email.")
            st.session_state.state = "reg_email"
            time.sleep(3)
            st.rerun()
    else:
        play_audio("Name not received. Let's try again.")
        time.sleep(2)
        st.rerun()

def reg_email_state():
    st.markdown('<div class="title-box">Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-indicator">Step 2 of 4: Email</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-box">Name: {st.session_state.tmp.get("name", "").title()}</div>', unsafe_allow_html=True)
    st.markdown('<div class="instruction-box">Say your email address slowly.<br>Say **"at"** for @ and **"dot"** for .</div>', unsafe_allow_html=True)
    
    play_audio("Step two of four. Say your email address slowly. Say at for @ symbol and dot for period. For example, say J O H N at G M A I L dot C O M.")
    
    email = listen_for_voice(wait_before_listen=4)
    
    if email:
        email_lower = email.lower()
        if match_command(email_lower, ["cancel", "back", "stop"]):
            play_audio("Going back to name.")
            st.session_state.state = "reg_name"
            time.sleep(2)
            st.rerun()
        else:
            # FIX: More robust replacements for 'at' and 'dot'
            # 1. Clean up common errors from speech recognition
            cleaned_email = (email_lower
                     .replace(" at sign ", " at ")
                     .replace(" dot com ", " dot com") 
                     .replace(" dot net ", " dot net") 
                     .replace(" dott ", " dot ")
                     .replace(" comma ", " dot ") # Common misrecognition
                     .replace(" dash ", "-")
                     .replace(" underscore ", "_")
                     .replace(" space ", "") # Clean up explicit "space"
                    )
            
            # 2. Now perform the main replacements and remove ALL remaining spaces
            email_processed = cleaned_email.replace(" at ", "@").replace(" dot ", ".").replace(" ", "")
            
            if not validate_email(email_processed):
                st.markdown('<div class="error-box">Invalid email format.</div>', unsafe_allow_html=True)
                play_audio("Invalid email format. Please say a valid email address.")
                time.sleep(3)
                st.rerun()
            else:
                st.session_state.tmp["email"] = email_processed
                st.markdown(f'<div class="success-box">Email: {email_processed}</div>', unsafe_allow_html=True)
                play_audio(f"Email {email_processed} saved. Proceeding to username.")
                st.session_state.state = "reg_user"
                time.sleep(3)
                st.rerun()
    else:
        play_audio("Email not received. Let's try again.")
        time.sleep(2)
        st.rerun()

def reg_user_state():
    st.markdown('<div class="title-box">Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-indicator">Step 3 of 4: Username</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-box">Email: {st.session_state.tmp.get("email", "")}</div>', unsafe_allow_html=True)
    st.markdown('<div class="instruction-box">Create a username using letters and numbers.</div>', unsafe_allow_html=True)
    
    play_audio("Step three of four. Say your desired username. Use letters and numbers only. Spaces will be removed. For example, say john 123.")
    
    username = listen_for_voice(wait_before_listen=4)
    
    if username:
        username_lower = username.lower()
        if match_command(username_lower, ["cancel", "back", "stop"]):
            play_audio("Going back to email.")
            st.session_state.state = "reg_email"
            time.sleep(2)
            st.rerun()
        else:
            username = username.replace(" ", "").lower()
            st.session_state.tmp["username"] = username
            st.markdown(f'<div class="success-box">Username: {username}</div>', unsafe_allow_html=True)
            play_audio(f"Username {username} saved. Proceeding to password.")
            st.session_state.state = "reg_pass"
            time.sleep(3)
            st.rerun()
    else:
        play_audio("Username not received. Let's try again.")
        time.sleep(2)
        st.rerun()

def reg_pass_state():
    st.markdown('<div class="title-box">Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-indicator">Step 4 of 4: Password</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-box">Username: {st.session_state.tmp.get("username", "")}</div>', unsafe_allow_html=True)
    st.markdown('<div class="instruction-box">Create a password with at least 6 characters.</div>', unsafe_allow_html=True)
    
    play_audio("Final step, step four of four. Say your password. It must be at least six characters long. Spaces will be removed.")
    
    password = listen_for_voice(wait_before_listen=4)
    
    if password:
        password_lower = password.lower()
        if match_command(password_lower, ["cancel", "back", "stop"]):
            play_audio("Going back to username.")
            st.session_state.state = "reg_user"
            time.sleep(2)
            st.rerun()
        else:
            password = password.replace(" ", "").lower()
            
            if not validate_password(password):
                st.markdown('<div class="error-box">Password too weak or too short.</div>', unsafe_allow_html=True)
                play_audio("Password is too weak or too short. Please use at least six characters and avoid common passwords.")
                time.sleep(4)
                st.rerun()
            else:
                name = st.session_state.tmp["name"]
                email = st.session_state.tmp["email"]
                username = st.session_state.tmp["username"]
                
                resp = db.add_user(name, email, username, password)
                
                if resp is True:
                    st.markdown('<div class="success-box"> Registration Successful!</div>', unsafe_allow_html=True)
                    play_audio(f"Congratulations! Registration successful. Welcome {name}. You can now login using username {username}. Returning to main menu.")
                    st.session_state.state = "welcome"
                    st.session_state.tmp = {}
                    time.sleep(6)
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-box">Registration Error</div>', unsafe_allow_html=True)
                    play_audio(f"{resp}. Please try again with different credentials.")
                    time.sleep(4)
                    st.session_state.state = "reg_user"
                    st.rerun()
    else:
        play_audio("Password not received. Let's try again.")
        time.sleep(2)
        st.rerun()

# ==================== LOGIN STATES ====================
def login_user_state():
    st.markdown('<div class="title-box">Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-indicator">Step 1 of 2: Username</div>', unsafe_allow_html=True)
    st.markdown('<div class="instruction-box">Say your registered username.</div>', unsafe_allow_html=True)
    
    play_audio("Login process. Step one of two. Please say your username.")
    
    username = listen_for_voice(wait_before_listen=4)
    
    if username:
        username_lower = username.lower()
        if match_command(username_lower, ["cancel", "back", "stop"]):
            play_audio("Cancelling login. Returning to main menu.")
            st.session_state.state = "welcome"
            time.sleep(2)
            st.rerun()
        else:
            username = username.replace(" ", "").lower()
            st.session_state.tmp["username"] = username
            st.markdown(f'<div class="success-box">Username: {username}</div>', unsafe_allow_html=True)
            play_audio(f"Username {username} received. Proceeding to password.")
            st.session_state.state = "login_pass"
            time.sleep(3)
            st.rerun()
    else:
        play_audio("Username not received. Let's try again.")
        time.sleep(2)
        st.rerun()

def login_pass_state():
    st.markdown('<div class="title-box">Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-indicator">Step 2 of 2: Password</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-box">Username: {st.session_state.tmp.get("username", "")}</div>', unsafe_allow_html=True)
    st.markdown('<div class="instruction-box">Say your password.</div>', unsafe_allow_html=True)
    
    play_audio("Step two of two. Please say your password.")
    
    password = listen_for_voice(wait_before_listen=4)
    
    if password:
        password_lower = password.lower()
        if match_command(password_lower, ["cancel", "back", "stop"]):
            play_audio("Going back to username.")
            st.session_state.state = "login_user"
            time.sleep(2)
            st.rerun()
        else:
            password = password.replace(" ", "").lower()
            username = st.session_state.tmp["username"]
            
            ok, res = db.check_user(username, password)
            
            if ok:
                name = res
                st.session_state.tmp["name"] = name
                st.markdown('<div class="success-box"> Login Successful!</div>', unsafe_allow_html=True)
                play_audio(f"Login successful! Welcome back {name}. You are now logged in.")
                st.session_state.state = "home"
                time.sleep(4)
                st.rerun()
            else:
                st.markdown('<div class="error-box">Login Failed</div>', unsafe_allow_html=True)
                play_audio(f"{res}. Please try again.")
                time.sleep(4)
                st.session_state.state = "login_user"
                st.rerun()
    else:
        play_audio("Password not received. Let's try again.")
        time.sleep(2)
        st.rerun()
