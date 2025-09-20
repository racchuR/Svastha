def check_spine_alignment(pose_landmarks):
    # Example: Use shoulder and hip points for alignment
    left_shoulder = pose_landmarks.landmark[11]
    right_shoulder = pose_landmarks.landmark[12]
    left_hip = pose_landmarks.landmark[23]
    right_hip = pose_landmarks.landmark[24]

    # Calculate average shoulder and hip y-coordinates
    avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    avg_hip_y = (left_hip.y + right_hip.y) / 2

    # If shoulders and hips are vertically aligned, posture is good
    if abs(avg_shoulder_y - avg_hip_y) < 0.1:
        return "good"
    else:
        return "poor"