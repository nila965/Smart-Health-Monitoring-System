def decode_gesture_code(code):
    """
    Decodes the Gesture Code (1-6) from ThingSpeak into human-readable text.
    Mapping based on user's hardware logic.
    """
    mapping = {
        0: "Normal",
        1: "EMERGENCY ALERT",
        2: "I am OK",
        3: "Need Water",
        4: "Need Food",
        5: "Call Doctor",
        6: "Take Medicine"
    }
    return mapping.get(int(code) if code is not None else 0, "Normal")

def classify_health_risk(data):
    """
    AI Risk Logic: Gesture Code 1 = Critical, others = Status-based decoding.
    """
    if data is None:
        return "Unknown", "grey", ["No data"], "None"

    bpm = data.get('BPM', 0)
    room_temp = data.get('Room_Temperature', 0)
    accel_z = data.get('Accel_Z', 0)
    gesture_code = data.get('Gesture_Code', 0)
    
    reasons = []
    gesture_msg = decode_gesture_code(gesture_code)
    
    # 1. Critical Trigger: Emergency Gesture Alert
    if gesture_msg == "EMERGENCY ALERT":
        reasons.append("USER TRIGGERED EMERGENCY GESTURE")
        return "Critical", "critical", reasons, gesture_msg

    # 2. Physiological Issues (Warning only, as per user's previous preference)
    # BPM Thresholds
    if (bpm > 140 or bpm < 50):
        reasons.append(f"Abnormal Pulse ({bpm} BPM)")
        
    if abs(accel_z) > 15:
        reasons.append("Irregular Motion Detected")

    # If it's a doctor call or medicine need, mark as Warning
    if gesture_msg in ["Call Doctor", "Take Medicine"]:
        reasons.append(f"Patient Request: {gesture_msg}")
        return "Warning", "warning", reasons, gesture_msg

    if reasons:
        return "Warning", "warning", reasons, gesture_msg
    
    return "Normal", "normal", ["System Stable"], gesture_msg

def get_risk_score(data):
    """
    Returns a numeric risk score (0-100) for visualization.
    """
    score = 0
    bpm = data.get('BPM', 75)
    temp = data.get('Room_Temperature', 37)
    
    # Calculate heart rate component
    if bpm > 100:
        score += min(50, (bpm - 100) * 2)
    elif bpm < 60:
        score += min(50, (60 - bpm) * 2)
        
    # Calculate temperature component
    if temp > 37.5:
        score += min(50, (temp - 37.5) * 10)
    elif temp < 36:
        score += min(50, (36 - temp) * 10)
        
    return min(100, score)
