# Main pipeline

# Example usage of pose matching
"""
from src.keypoint_templates import TemplateManager
from src.pose_matching import PoseMatcher
from src.normalization import normalize_keypoints

# Assume 'detected_keypoints' is obtained from MediaPipe and is a dictionary {landmark_name: [x, y]}
detected_keypoints = {
    'nose': [320, 240],
    'left_eye': [315, 235],
    'right_eye': [325, 235],
    'left_shoulder': [300, 250],
    'right_shoulder': [340, 250],
    # ... (other keypoints)
}

# Load templates
template_manager = TemplateManager()
template_manager.load_templates('data/templates/')

# Match pose
pose_matcher = PoseMatcher(threshold=0.5)
best_match_name, min_distance = pose_matcher.match_pose(detected_keypoints, template_manager.templates)

if best_match_name:
    print(f"Best matched pose: {best_match_name} with a distance of {min_distance}")
else:
    print("No matching pose found within the threshold.")
"""

# Possible Mediapipe usage
"""
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Assuming 'image' is your input image
results = pose.process(image)

if results.pose_landmarks:
    detected_keypoints = {}
    for idx, landmark in enumerate(results.pose_landmarks.landmark):
        landmark_name = mp_pose.PoseLandmark(idx).name.lower()
        detected_keypoints[landmark_name] = [landmark.x, landmark.y]
"""