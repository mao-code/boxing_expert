import cv2
import mediapipe as mp
import json
import argparse
import os

def extract_keypoints_from_image(image_path: str, output_json: str) -> None:
    """
    Extract pose keypoints from a single image and save them to a JSON file
    in the same format as the KeypointExtractor class produces.
    
    Format example:
    {
       "nose": [0.3, 0.4],
       "left_eye_inner": [0.35, 0.45],
       ...
    }

    Args:
        image_path (str): Path to the input image file.
        output_json (str): Path to the output JSON file.
    """
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")

    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image with MediaPipe Pose
    results = pose.process(image_rgb)
    
    # Prepare a dictionary to store the keypoints
    keypoints = {}

    if results.pose_landmarks:
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmark_name = mp_pose.PoseLandmark(idx).name.lower()
            keypoints[landmark_name] = [landmark.x, landmark.y]

    # Write keypoints to a JSON file
    with open(output_json, 'w') as f:
        json.dump(keypoints, f, indent=4)

    print(f"Keypoints saved to {output_json}")

def main():
    parser = argparse.ArgumentParser(
        description="Extract pose keypoints from a single image and save them to JSON."
    )
    parser.add_argument("image_path", type=str, help="Path to the input image file.")
    parser.add_argument(
        "--output_json",
        type=str,
        default="output_keypoints.json",
        help="Path to the output JSON file (default: output_keypoints.json).",
    )
    args = parser.parse_args()

    extract_keypoints_from_image(args.image_path, args.output_json)

if __name__ == "__main__":
    main()

# python3 test/template_extraction.py "data/frames_img/frame_0010.jpg" --output_json "data/templates/cross.json"