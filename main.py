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

from src.keypoint_extractor import KeypointExtractor
from src.keypoint_templates import TemplateManager
from src.pose_matching import PoseMatcher
from src.normalization import normalize_keypoints
from src.analyzer import analyze_all
import sys
from PyQt5.QtWidgets import QApplication
from src.UI import BoxingApp

VIDEO_PATH = r'data/videos/test1.mp4'
FRAMES_PATH = r'data/frames_img'
FRAME_INTERVAL = 10
MAX_FRAME = 300
TEMPLATE_PATH = r'data/templates'
THRESHOLD = 0.5

'''
# Initialize the extractor
extractor = KeypointExtractor(VIDEO_PATH, FRAME_INTERVAL, MAX_FRAME, FRAMES_PATH)

# Extract keypoints and frames (frames will be saved in the specified directory)
keypoints_per_frame = extractor.extract_keypoints_from_video()

# Load templates
template_manager = TemplateManager()
template_manager.load_templates(TEMPLATE_PATH)

# Compare keypoints to templates and match poses
pose_matcher = PoseMatcher(threshold=THRESHOLD)  # Set the matching threshold

for frame_idx, keypoints in enumerate(keypoints_per_frame):
    print(f"Processing frame {frame_idx + 1}...")

    # Match pose with the templates
    best_match_name, min_distance = pose_matcher.match_pose(keypoints, template_manager.templates)

    if best_match_name:
        print(f"Frame {frame_idx + 1}: Best matched pose: {best_match_name} with a distance of {min_distance}")
    else:
        print(f"Frame {frame_idx + 1}: No matching pose found within the threshold.")
'''

results = analyze_all(VIDEO_PATH, TEMPLATE_PATH, FRAME_INTERVAL, MAX_FRAME, THRESHOLD, FRAMES_PATH)
# print(results)

app = QApplication(sys.argv)
mainWin = BoxingApp()

# mainWin.set_results(results)
mainWin.set_realTime_mode(True) # 如果要 upload 其他影片開這個

mainWin.set_interval(FRAME_INTERVAL)
mainWin.show()
sys.exit(app.exec_())