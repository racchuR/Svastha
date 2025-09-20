import cv2
import mediapipe as mp
import time
import numpy as np
import os
import pygame
os.environ['SDL_AUDIODRIVER'] = 'directsound'
pygame.mixer.init()
from threading import Thread
import math

# Initialize MediaPipe components
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize pygame for audio alerts
pygame.mixer.init()

# Load audio files (replace with your actual file paths)
ALERT_SOUNDS = {
    'spine': r'C:\Users\HP\OneDrive\Desktop\spine.wav',
    'neck': r'C:\Users\HP\OneDrive\Desktop\neck.wav',
    'eyes': r'C:\Users\HP\OneDrive\Desktop\eyes.wav'
}
CHANT_START_SOUND = r'C:\Users\HP\OneDrive\Desktop\start_chant.wav'
CHANT_END_SOUND = r'C:\Users\HP\OneDrive\Desktop\end_chant.wav'
# Chanting parameters
CHANT_START_SOUND = 'start_chant.wav'
CHANT_END_SOUND = 'end_chant.wav'
MIN_CHANT_DURATION = 5  # seconds
MAX_CHANT_DURATION = 20  # seconds

class OmChantingGuide:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.chant_start_time = None
        self.chant_duration = 0
        self.last_alert_time = {
            'spine': 0,
            'neck': 0,
            'eyes': 0
        }
        self.alert_cooldown = 3
        self.chanting_active = False
        self.posture_status = "Unknown"
        self.eyes_status = "Unknown"
        
        self.alert_active = {
        'spine': False,
        'neck': False,
        'eyes': False
    }
       
  # seconds between alerts
        
    def calculate_spine_alignment(self, landmarks):
        """Calculate spine alignment using shoulder and hip positions"""
        # Get key points
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        
        # Calculate midpoint of shoulders and hips
        shoulder_mid = ((left_shoulder.x + right_shoulder.x)/2, 
                        (left_shoulder.y + right_shoulder.y)/2)
        hip_mid = ((left_hip.x + right_hip.x)/2, 
                   (left_hip.y + right_hip.y)/2)
        
        # Calculate vertical alignment (should be close to 0 when straight)
        vertical_offset = abs(shoulder_mid[0] - hip_mid[0])
        
        # Calculate horizontal alignment (shoulders should be level)
        shoulder_alignment = abs(left_shoulder.y - right_shoulder.y)
        
        return vertical_offset < 0.05 and shoulder_alignment < 0.03
    
    def calculate_head_alignment(self, landmarks):
        """Calculate head/neck position using nose and shoulders"""
        nose = landmarks[mp_pose.PoseLandmark.NOSE]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Calculate shoulder midpoint
        shoulder_mid = ((left_shoulder.x + right_shoulder.x)/2, 
                        (left_shoulder.y + right_shoulder.y)/2)
        
        # Calculate distance between nose and shoulder midpoint
        distance = math.sqrt((nose.x - shoulder_mid[0])**2 + 
                             (nose.y - shoulder_mid[1])**2)
        
        # Check if head is centered (should be within threshold)
        return distance < 0.15
    
    def are_eyes_open(self, face_landmarks):
        """Determine if eyes are open using eye landmarks"""
        # Get eye landmarks (simplified version)
        left_eye = [face_landmarks[i] for i in [33, 160, 158, 133, 153, 144]]
        right_eye = [face_landmarks[i] for i in [362, 385, 387, 263, 373, 380]]
        
        # Calculate eye aspect ratio (EAR)
        def eye_aspect_ratio(eye):
            # Compute the euclidean distance between vertical eye landmarks
            v1 = math.sqrt((eye[1].x - eye[5].x)**2 + (eye[1].y - eye[5].y)**2)
            v2 = math.sqrt((eye[2].x - eye[4].x)**2 + (eye[2].y - eye[4].y)**2)
            # Compute the euclidean distance between horizontal eye landmarks
            h = math.sqrt((eye[0].x - eye[3].x)**2 + (eye[0].y - eye[3].y)**2)
            # Compute the eye aspect ratio
            ear = (v1 + v2) / (2.0 * h)
            return ear
        
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        
        # Average EAR for both eyes
        ear = (left_ear + right_ear) / 2.0
        
        # Eyes are open if EAR is above threshold (adjust as needed)
        return ear > 0.25
    
    def play_alert(self, alert_type):
        """Play audio alert with cooldown"""
        current_time = time.time()
        if current_time - self.last_alert_time[alert_type] > self.alert_cooldown:
            try:
                pygame.mixer.Sound(ALERT_SOUNDS[alert_type]).play()
                self.last_alert_time[alert_type] = current_time
            except:
                print(f"Alert: {alert_type}")  # Fallback to text

    def update_alerts(self, spine_ok, head_ok, eyes_open):
    if not spine_ok and not self.alert_active['spine']:
        self.play_alert('spine')
        self.alert_active['spine'] = True
    elif spine_ok:
        self.alert_active['spine'] = False

    if not head_ok and not self.alert_active['neck']:
        self.play_alert('neck')
        self.alert_active['neck'] = True
    elif head_ok:
        self.alert_active['neck'] = False

    if eyes_open and not self.alert_active['eyes']:
        self.play_alert('eyes')
        self.alert_active['eyes'] = True
    elif not eyes_open:
        self.alert_active['eyes'] = False

    def start_chant(self):
        if not self.chanting_active:
            self.chant_start_time = time.time()
            pygame.mixer.Sound(CHANT_START_SOUND).play()
            self.chanting_active = True
            print("Chanting started")

    def end_chant(self):
        if self.chanting_active:
            self.chant_duration = time.time() - self.chant_start_time
            pygame.mixer.Sound(CHANT_END_SOUND).play()
            print(f"Chanting duration: {self.chant_duration:.2f} seconds")
            self.chant_start_time = None
            self.chanting_active = False
            return self.chant_duration
        return 0
    
    def run(self):
        """Main processing loop"""
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            pose_results = pose.process(rgb_frame)
            face_results = face_mesh.process(rgb_frame)
            
            # Check posture if pose landmarks detected
            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                spine_ok = self.calculate_spine_alignment(landmarks)
                self.posture_status = "Good" if spine_ok else "Bad"
    
                head_ok = self.calculate_head_alignment(landmarks)

            if face_results.multi_face_landmarks:
                 for face_landmarks in face_results.multi_face_landmarks:
                     eyes_open = self.are_eyes_open(face_landmarks.landmark)
                     self.eyes_status = "Open" if eyes_open else "Closed"
            self.update_alerts(spine_ok,head_ok,eyes_open)

            
            # Display the frame (optional for debugging)
            cv2.imshow('Om Chanting Guide', frame)
            
            
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
    def get_status(self):
        return {
            "posture": self.posture_status,
            "eyes": self.eyes_status,
            "chanting_active": self.chanting_active,
            "chant_duration": time.time() - self.chant_start_time if self.chanting_active else 0
    }

        

if __name__ == "__main__":
    guide = OmChantingGuide()
    guide.run()
