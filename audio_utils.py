# audio_utils.py

import streamlit as st
from gtts import gTTS
import tempfile
import os
import time
import speech_recognition as sr
import atexit
import glob

# Cleanup logic for temp files
def cleanup_temp_files():
    temp_dir = tempfile.gettempdir()
    for file in glob.glob(os.path.join(temp_dir, "tmpz*.mp3")):
        try: os.remove(file)
        except: pass
atexit.register(cleanup_temp_files)

# --- Reusable Audio Functions ---

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', prefix='tmpz')
        file_path = temp_file.name
        temp_file.close()
        tts.save(file_path)
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format='audio/mp3', autoplay=True)
        words = len(text.split())
        wait_time = max(3, words * 0.5)
        time.sleep(wait_time)
    except Exception as e:
        print(f"Audio error: {e}")

def show_countdown(seconds):
    cd = st.empty()
    for i in range(seconds, 0, -1):
        cd.markdown(f'<div class="countdown-timer">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    cd.empty()

def listen_for_voice(wait_before_listen=3):
    st.markdown('<div class="waiting-box">Preparing to record...</div>', unsafe_allow_html=True)
    show_countdown(wait_before_listen)
    
    listening_msg = st.empty()
    listening_msg.markdown('<div class="listening-box">🎤 LISTENING NOW... SPEAK CLEARLY AND LOUDLY</div>', unsafe_allow_html=True)
    
    try:
        recognizer = sr.Recognizer()
        
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        
        with sr.Microphone() as source:
            st.info("🎧 Calibrating microphone... Please wait (3 seconds)...")
            recognizer.adjust_for_ambient_noise(source, duration=3)
            st.success(f" Ready! Energy level: {recognizer.energy_threshold}")
            
            listening_msg.markdown('<div class="listening-box">🔴 RECORDING... SPEAK NOW!</div>', unsafe_allow_html=True)
            
            try:
                audio = recognizer.listen(source, timeout=25, phrase_time_limit=20)
                listening_msg.markdown('<div class="waiting-box"> Processing speech...</div>', unsafe_allow_html=True)
                
                text = recognizer.recognize_google(audio)
                listening_msg.empty()
                st.markdown(f'<div class="success-box"> You said: {text}</div>', unsafe_allow_html=True)
                play_audio(f"You said {text}")
                time.sleep(1)
                return text.strip()
                
            except sr.WaitTimeoutError:
                listening_msg.empty()
                st.markdown('<div class="error-box"> No speech detected within time limit</div>', unsafe_allow_html=True)
                play_audio("I did not hear any speech. Please speak louder and closer to your microphone.")
                time.sleep(3)
                return ""
                
            except sr.UnknownValueError:
                listening_msg.empty()
                st.markdown('<div class="error-box"> Could not understand your voice</div>', unsafe_allow_html=True)
                play_audio("Sorry, I could not understand what you said. Please speak more clearly, slowly, and loudly.")
                time.sleep(3)
                return ""
                
            except (sr.RequestError, OSError, Exception) as e:
                listening_msg.empty()
                st.markdown(f'<div class="error-box"> Error: {str(e)}</div>', unsafe_allow_html=True)
                play_audio(f"An error occurred. {str(e)}")
                time.sleep(3)
                return ""
                
    except Exception as e:
        listening_msg.empty()
        st.markdown(f'<div class="error-box"> Fatal Error: {str(e)}</div>', unsafe_allow_html=True)
        play_audio(f"A fatal error occurred. {str(e)}")
        time.sleep(3)
        return ""

def match_command(text, keywords):
    if not text: return False
    text_lower = text.lower()
    if isinstance(keywords, list):
        return any(keyword.lower() in text_lower for keyword in keywords)
    return keywords.lower() in text_lower