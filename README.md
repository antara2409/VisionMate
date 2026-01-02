# VisionMate  
**AI-Powered Assistive Mobility Tool for Visually Impaired Users**

VisionMate is a research-oriented assistive vision system designed to enhance environmental awareness for visually impaired individuals through frame-level video analysis and voice-based interaction.

The system processes videos sequentially without skipping frames, detects surrounding objects using deep learning, and provides auditory feedback to support safer navigation and situational understanding.

---

## Motivation

Most real-time vision systems prioritize speed by skipping frames, which can lead to missed transient or fast-moving objects. In assistive applications, such omissions can compromise user safety.

VisionMate was developed with a **safety-first philosophy**, emphasizing:
- Complete frame-level analysis
- Accessibility through voice-first interaction
- Reliability over raw throughput

---

## Key Features

- Frame-by-frame video analysis without skipping frames  
- Real-time object detection using a fine-tuned YOLOv8 model  
- Voice-based interaction for accessibility  
- Audio feedback describing detected objects  
- Start / Pause / Resume / Stop execution controls  
- Modular and extensible system architecture  

---

## System Architecture Overview

VisionMate follows a layered, modular architecture:

1. **User Interface Layer**  
   Built using Streamlit to manage user interaction, video upload, and execution control.

2. **Video Processing Layer**  
   OpenCV extracts and processes video frames sequentially.

3. **Object Detection Layer**  
   Each frame is passed to a fine-tuned YOLOv8 model to detect objects and generate bounding boxes.

4. **Feedback Generation Layer**  
   Detection results are converted into concise textual descriptions.

5. **Audio Output Layer**  
   Textual feedback is converted into speech to enable hands-free interaction.

---

## Technology Stack

| Category | Tools / Libraries |
|--------|------------------|
| Programming Language | Python |
| Web Framework | Streamlit |
| Computer Vision | OpenCV |
| Object Detection | YOLOv8 (Ultralytics) |
| Numerical Processing | NumPy |
| Speech Processing | Speech Recognition, gTTS |
| Model Training | Google Colab (GPU) |
| Utilities | OS, Tempfile, Time |

---

## Model Training & Fine-Tuning

Due to local hardware constraints, model fine-tuning was performed using **Google Colab** with GPU acceleration.

- Base model: YOLOv8 (nano variant)  
- Training performed across multiple epochs  
- Evaluation metrics included precision, recall, and mAP  
- The best performing checkpoint (`best.pt`) was exported and integrated into the application for inference  

This approach enabled efficient experimentation while maintaining deployment feasibility on limited hardware.

---

## Installation
```bash
git clone https://github.com/antara2409/VisionMate.git
cd VisionMate
pip install -r requirements.txt
```
---
## Running the Application
```bash
streamlit run app.py
```

Upload a video file through the interface and control analysis using voice or UI commands.
---
## Known Limitations

- Frame-level processing introduces latency for long videos
- Performance depends on available hardware resources
- Audio feedback granularity is limited by detection confidence
- Currently supports offline video analysis only
---
## Future Work

- Live camera stream support
- Adaptive frame processing based on scene dynamics
- Spatial reasoning for navigation guidance
- Multilingual audio feedback
- Integration with wearable devices
---
## Ethical Considerations

VisionMate is intended as an assistive support system and not a replacement for human judgment. The system prioritizes safety, transparency, and accessibility in its design.

