# app.py - STREAMLINED MAIN APPLICATION

import streamlit as st
import database as db
import time
import cv2
import os
import tempfile

# Import functions from modules
from audio_utils import play_audio, listen_for_voice, match_command
from voice_auth import (
    welcome_state, reg_name_state, reg_email_state, reg_user_state, reg_pass_state,
    login_user_state, login_pass_state
)
from vision_core import load_model, extract_yolov8_data, generate_feedback

# --- Streamlit Setup and Styling ---
st.set_page_config(
    page_title="VisionMate: Navigate with Clarity, Live with Freedom",
    page_icon="🔒",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
body, .stApp, input, button, textarea { font-family: 'Poppins', sans-serif; }
/* ... (Rest of your CSS styles here) ... */
.title-box { font-size: 3.0rem; font-weight: 700; color: #2a3e64; text-align: center; padding: 2.5rem 0 0.5rem 0; background: #ffffffec; border-radius: 20px; margin: 2rem 0 0.5rem 0; border: 2px solid #cad5e6; box-shadow: 0 4px 24px #c7cbde88; }
.slogan-box { font-size: 1.5rem; font-weight: 400; color: #4f6fa7; text-align: center; padding: 1rem 0; margin-top: 0; margin-bottom: 0.5rem; background: #f6fafe; border-radius: 12px; }
.status-box, .step-indicator, .success-box, .error-box, .waiting-box, .instruction-box { display: block; margin: 1.3rem 0; border-radius: 13px; box-shadow: 0 2px 10px #b1bdd648; padding: 1.2rem 1.6rem; font-weight: 500; font-size: 1.48rem; }
.status-box      { background: #f5f7fa; border: 1.5px solid #cfd8e3; color: #334e68; }
.step-indicator{ background: #eaecef; border: 1.2px solid #bbc7da; color: #445dad; }
.success-box   { background: #e7fee6; border: 1.2px solid #70c282; color: #336b37; }
.error-box     { background: #ffe3e3; border: 1.2px solid #fc7676; color: #a73737; }
.waiting-box   { background: #f4faff; border: 1.2px solid #b2dfef; color: #52727e; }
.instruction-box { background: #f5f6fb; border: 1.2px solid #b0c3e3; color: #465172; }
.countdown-timer { font-size: 2.3rem; color: #4052b5; padding: 1.1rem 0; background: #f5f7fa; border-radius: 11px; font-weight: 600; margin-bottom: 0.6rem; }
.listening-box { background: #ecf0fe; border: 1.1px solid #99a7fc; color: #4052b5; font-size:1.35rem; font-weight:600; margin-top:0.7rem;}
</style>
""", unsafe_allow_html=True)

# Initialize session state

if 'state' not in st.session_state:
    st.session_state.state = "welcome"
if 'tmp' not in st.session_state:
    st.session_state.tmp = {}
if 'audio_enabled' not in st.session_state:
    st.session_state.audio_enabled = True
   
# --- NEW VARIABLES FOR PAUSE/RESUME ---
if 'is_paused' not in st.session_state:
    st.session_state.is_paused = False
if 'last_frame_index' not in st.session_state:
    st.session_state.last_frame_index = 0
# ---------------------------------------

db.init_db()

# ==================== HOME STATE (Final Voice Flow) ====================

def home_state():
    name = st.session_state.tmp.get("name", "User")
    st.markdown(f'<div class="title-box">Welcome Home, {name.title()}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="success-box"> Logged in as: {name.title()}</div>', unsafe_allow_html=True)
   
    # Visual instruction
    st.markdown('<div class="instruction-box">Say "Analyze Video" to process a file.<br>Say "Logout" to sign out.</div>', unsafe_allow_html=True)

    # Audio instruction (Complete and clear)
    play_audio(f"Welcome {name}. Say Analyze Video to process a file, or say Logout to sign out.")

    # Listen for voice command
    cmd = listen_for_voice(wait_before_listen=4)
   
    if cmd:
        cmd_lower = cmd.lower()
       
        # --- FIX: Added "analyse video" for robust command matching ---
        if match_command(cmd_lower, [
            "analyze video",
            "analyse video",
            "upload video",
            "process file"
        ]):
            play_audio("Proceeding to video analysis.")
            st.session_state.state = "upload_video"
           
        elif match_command(cmd_lower, ["logout", "sign out", "log out", "stop"]):
            play_audio("Logging out. Shutting down Visionmate. See you next time!")
            st.session_state.state = "welcome"
            st.session_state.tmp = {}
           
        else:
            play_audio("Sorry, I couldn't understand. Please say Analyze Video or Logout.")
            time.sleep(2)
       
        time.sleep(2)
        st.rerun()
    else:
        # Rerun to keep listening if no command was received
        st.rerun()

# ==================== UPLOAD VIDEO STATE (Manual Upload and Stable Flow) ====================

def upload_video_state():
    model = load_model()
    name = st.session_state.tmp.get("name", "User")
    
    # Initialize necessary session state variables
    if 'video_to_process' not in st.session_state.tmp:
        st.session_state.tmp['video_to_process'] = None
        st.session_state.last_frame_index = 0
        st.session_state.is_paused = False
        st.session_state.stop_triggered = False # Flag to handle deletion safely
        
    st.markdown(f'<div class="title-box">VisionMate Video Analysis</div>', unsafe_allow_html=True)

    # --- UI CONTROL BAR ---
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # 1. Audio Toggle
    st.session_state.audio_enabled = col1.checkbox("🔊 Audio Feedback", value=st.session_state.audio_enabled)

    # 2. Stop Button (Sets a flag, cleanup happens outside the locked process)
    if col3.button("🔴 Stop & Home"):
        st.session_state.stop_triggered = True
        st.session_state.is_paused = False # Break pause to allow cleanup
        st.rerun()

    # 3. Pause/Resume Button
    if st.session_state.tmp['video_to_process'] is not None:
        if st.session_state.is_paused:
            if col2.button("▶️ Resume"):
                st.session_state.is_paused = False
                play_audio("Resuming.")
                st.rerun()
        else:
            if col2.button("⏸️ Pause"):
                st.session_state.is_paused = True
                play_audio("Paused.")
                # We don't rerun here; the loop will catch the change

    # --- PHASE 1: FILE UPLOADER ---
    if st.session_state.tmp['video_to_process'] is None:
        uploaded_file = st.file_uploader("Upload Video", type=['mp4', 'avi', 'mov'])
        if uploaded_file:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name)
            tfile.write(uploaded_file.read())
            tfile.close()
            st.session_state.tmp['video_to_process'] = tfile.name
            st.session_state.last_frame_index = 0
            st.rerun()
        return

    # --- PHASE 2: PROCESSING LOOP ---
    video_path = st.session_state.tmp['video_to_process']
    cap = cv2.VideoCapture(video_path)
    
    # CRITICAL: Jump to the last saved frame index
    if st.session_state.last_frame_index > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, st.session_state.last_frame_index)
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    FRAME_WINDOW = st.empty()
    feedback_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    feedback_last = ""
    
    # Only run the loop if not paused and not stopped
    if not st.session_state.is_paused and not st.session_state.stop_triggered:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: 
                break # Video ended
            
            # Update current frame index
            current_idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            st.session_state.last_frame_index = current_idx

            # UI Interruption Check (Streamlit reruns on interaction)
            if st.session_state.is_paused or st.session_state.stop_triggered:
                break

            # AI Detection Logic
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(img)[0]
            results_object, detections_array = extract_yolov8_data(results)
            
            # Display
            FRAME_WINDOW.image(results_object.plot(), width=640)
            
            # Feedback
            msg = generate_feedback(results_object, detections_array, frame_width, frame_height)
            feedback_placeholder.markdown(f'<div class="status-box">🤖 {msg}</div>', unsafe_allow_html=True)
            
            if msg != feedback_last and st.session_state.audio_enabled:
                play_audio(msg)
                feedback_last = msg
            
            progress_bar.progress(current_idx / total_frames)
            time.sleep(0.01)

    # --- PHASE 3: CLEANUP & STATE TRANSITION ---
    cap.release() # RELEASE THE LOCK FIRST (Fixes WinError 32)

    # Handle Stop/Home Action
    if st.session_state.stop_triggered:
        if os.path.exists(video_path):
            os.remove(video_path)
        st.session_state.tmp = {}
        st.session_state.state = "home"
        st.session_state.stop_triggered = False
        st.rerun()

    # Handle Natural Completion
    if st.session_state.last_frame_index >= total_frames - 1:
        if os.path.exists(video_path):
            os.remove(video_path)
        st.session_state.tmp['video_to_process'] = None
        st.success("Analysis Complete!")
        play_audio("Analysis complete.")
        time.sleep(2)
        st.session_state.state = "home"
        st.rerun()

    # If paused, the script ends here and waits for the user to click "Resume"
# ==================== MAIN APPLICATION RUNNER ====================
def main():
    state = st.session_state.state
   
    # ----------------------------------------------------
    # Check the state and run the corresponding function
    # ----------------------------------------------------
    if state == "welcome":
        welcome_state()
       
    # --- Registration Flow ---
    elif state == "reg_name":
        reg_name_state()
    elif state == "reg_email":
        reg_email_state()
    elif state == "reg_user":
        reg_user_state()
    elif state == "reg_pass":
        reg_pass_state()
       
    # --- Login Flow ---
    elif state == "login_user":
        login_user_state()
    elif state == "login_pass":
        login_pass_state()
       
    # --- Main Application Flow ---
    elif state == "home":
        home_state()
    elif state == "upload_video":
        upload_video_state()
       
    # --- Fallback ---
    else:
        st.session_state.state = "welcome"
        st.rerun()

if __name__ == "__main__":
    main()
