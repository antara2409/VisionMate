# vision_core.py
import streamlit as st
import numpy as np
from ultralytics import YOLO
from audio_utils import play_audio

# --- Model Loading and Detection Extraction ---

@st.cache_resource
def load_model():
    # 1. Load the model using the correct standard name: best.pt
    MODEL_PATH = "fine_tuned_weights/best.pt"
    
    # Load the specialized YOLOv8 model
    model = YOLO(MODEL_PATH) 
    
    return model

def extract_yolov8_data(results):
    """
    Extracts detection data from YOLOv8 Results object into the
    format expected by generate_feedback().
    Format: [x_min, y_min, x_max, y_max, confidence, class_index]
    """
    if not results or not results.boxes or len(results.boxes.xyxy) == 0:
        return results, None

    boxes = results.boxes.xyxy.cpu().numpy()
    confidences = results.boxes.conf.cpu().numpy()
    classes = results.boxes.cls.cpu().numpy()
    
    detections = []
    for box, conf, cls in zip(boxes, confidences, classes):
        detections.append(list(box) + [conf, cls])

    return results, np.array(detections)

# --- Core Feedback Generation Logic ---

def generate_feedback(results, detections, frame_width, frame_height):
    """
    Analyzes YOLO results to generate prioritized, actionable, and detailed audio feedback,
    including critical hazard warnings and comprehensive navigational cues.
    """
    labels = results.names
    
    if detections is None or len(detections) == 0:
        return "Path clear. Proceeding."

    # 1. Define Priority Categories (Updated for Navigational Path)
    CRITICAL_HAZARDS = [
        "blind_road", "ashcan", "fire_hydrant", "pole", "reflective_cone", "warning_column", 
    ]
    
    STOP_HAZARDS = [
        "person", "car", "bus", "truck", "motorcycle", "tricycle", "bicycle", 
    ]
    
    TRAFFIC_CONTROL = ["red_light", "stop sign"]
    GO_CONTROL = ["green_light"]
    
    PATH_GUIDANCE = ["crosswalk", "sign", "sidewalk", "square", "intersection", "bridge"] 
    # Includes new structural and path elements

    # --- Prepare all Detections for Scoring ---
    prioritized_detections = []
    has_red_signal = False
    has_green_signal = False
    has_sidewalk_or_blind_road = False # NEW: Path Confirmation Flag

    for detection in detections:
        x_min, y_min, x_max, y_max, conf, cls = detection
        label = labels[int(cls)]
        
        # Calculate scores and direction (UNCHANGED LOGIC)
        box_area = (x_max - x_min) * (y_max - y_min)
        proximity_score = y_max * box_area
        
        center_x = (x_min + x_max) / 2
        direction = "ahead" # Changed to 'ahead' for clearer GPS voice
        if center_x < frame_width * 0.35: direction = "to the left"
        elif center_x > frame_width * 0.65: direction = "to the right"
            
        proximity_text = "in the distance"
        priority_multiplier = 1
        if y_max > frame_height * 0.8:
            proximity_text = "VERY CLOSE"
            priority_multiplier = 4
        elif y_max > frame_height * 0.6:
            proximity_text = "nearby"
            priority_multiplier = 2

        # Priority Weight based on Object Type
        priority_weight = 1
        if label in CRITICAL_HAZARDS: priority_weight = 5
        elif label in STOP_HAZARDS: priority_weight = 3
        elif label in TRAFFIC_CONTROL: priority_weight = 4 

        final_score = proximity_score * priority_multiplier * priority_weight

        # Set control flags and path confirmation
        if label in TRAFFIC_CONTROL: has_red_signal = True
        if label in GO_CONTROL: has_green_signal = True
        if label in ["sidewalk", "blind_road"]: has_sidewalk_or_blind_road = True
        
        prioritized_detections.append({
            "label": label,
            "score": final_score,
            "direction": direction,
            "proximity": proximity_text,
            "is_critical": label in CRITICAL_HAZARDS,
            "requires_stop": label in STOP_HAZARDS or label in CRITICAL_HAZARDS or label in TRAFFIC_CONTROL,
            "is_turn_cue": label in ["intersection", "square"] and direction != "ahead"
        })

    # 2. Select the Top Priority Hazard/Object
    if not prioritized_detections:
        return "Path clear. Proceeding."

    prioritized_detections.sort(key=lambda x: x['score'], reverse=True)
    top_detection = prioritized_detections[0]
    
    # 3. Enhanced Navigational Feedback Generation

    # --- A. IMMEDIATE STOP / TRAFFIC CONTROL LOGIC (Highest Priority) ---
    
    if top_detection['label'] in TRAFFIC_CONTROL or top_detection['label'] == "red_light":
        return f"🛑 STOP! Traffic signal is RED {top_detection['direction']}."

    if top_detection['is_critical'] and top_detection['proximity'] == "VERY CLOSE":
        return f"🚨 EXTREME WARNING! {top_detection['label']} {top_detection['direction']}! STOP NOW!"
        
    if top_detection['requires_stop'] and top_detection['proximity'] in ["VERY CLOSE", "nearby"]:
        return f"HAZARD ALERT: {top_detection['label']} {top_detection['direction']} and {top_detection['proximity']}."

    # --- B. PATH CONFIRMATION AND TURN GUIDANCE (Focusing on Sequence) ---

    # 1. Turn Inference (Highest Navigational Priority)
    if top_detection['is_turn_cue'] and top_detection['proximity'] != "VERY CLOSE":
        turn_direction = top_detection['direction'].replace('to the ', '') # e.g., 'left'
        
        # Check if the path is clear ahead to suggest approaching the turn
        if not has_red_signal and not top_detection['requires_stop']:
            return f"Navigation: Approach the turn. An {top_detection['label']} is {top_detection['direction']}. Prepare to turn {turn_direction}."

    # 2. Bridge Guidance
    if top_detection['label'] == "bridge":
        if top_detection['proximity'] == "VERY CLOSE":
             return f"Structural update: Entering bridge now. Maintain steady path."
        elif top_detection['proximity'] == "nearby":
             return f"Attention! Approaching bridge {top_detection['direction']}."
        
    # 3. Crosswalk Guidance
    if top_detection['label'] == "crosswalk":
        if has_green_signal:
            return f"Navigation update: Clear to proceed. Crosswalk {top_detection['direction']}."
        else:
            return f"Crosswalk detected. Wait for signal or verbal confirmation."

    # 4. Path Confirmation
    if not has_sidewalk_or_blind_road:
        # If we can't detect the path, warn the user
        return "Guidance Note: Path (sidewalk/blind road) not detected. Proceed with caution."

    # --- C. PROCEED / ALL CLEAR LOGIC (Lowest Priority) ---
    
    if has_green_signal:
        return "Proceed. Green light ahead."
        
    # Announce the highest score item if it's not critical but provides context (e.g., 'tree')
    if top_detection['proximity'] == "nearby":
         return f"Path context: A {top_detection['label']} is {top_detection['direction']}."
         
    return "Path clear. Proceeding safely."