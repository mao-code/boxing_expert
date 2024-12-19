import os
import cv2
import shutil
import mediapipe as mp
import numpy as np
from typing import Dict, List


class KeypointExtractor:
    def __init__(self, video_path: str, frame_interval: int = 1, max_frames: int = None, frames_dir: str = None):
        """
        Args:
            video_path (str): Path to the input video file.
            frames_dir (str): Directory where frames will be saved, if saveImg2file is True.
            frame_interval (int): Interval to control how often frames are extracted.
            max_frames (int): Maximum number of frames to extract from the video. If None, all frames will be processed.
        """
        self.video_path = video_path
        self.frame_interval = frame_interval
        self.max_frames = max_frames
        self.frames_dir = frames_dir
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Error: Couldn't open video {self.video_path}")

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Initialize Mediapipe Pose model
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

    def extract_keypoints(self, frame: np.ndarray) -> Dict[str, List[float]]:
        """
        Extract pose keypoints from a single frame.
        Args: frame (np.ndarray): The input image (OpenCV format).
        Returns: Dict[str, List[float]]: Keypoints dictionary with {keypoint_name: [x, y]}.
        """

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        keypoints = {}
        if results.pose_landmarks:
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                landmark_name = self.mp_pose.PoseLandmark(idx).name.lower()
                keypoints[landmark_name] = [landmark.x, landmark.y]

        return keypoints

    def extract_keypoints_from_video(self, saveImg:bool = True) -> List[Dict[str, List[float]]]:
        """
        Extract keypoints from the video, optionally saving frames as images.
        Args: saveImg2file (bool): Whether to save frames as images. Default is True.
        Returns: List[Dict[str, List[float]]]: A list of keypoints dictionaries for each frame.
        """
        keypoints_per_frame = []
        frame_count = 0
        saved_frame_count = 0

        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                if self.max_frames and frame_count >= self.max_frames:
                    break

                if saveImg and not os.path.exists(self.frames_dir):
                    os.makedirs(self.frames_dir)  # Create the directory to save frames if needed

                if frame_count % self.frame_interval == 0:

                    # Extract keypoints for the current frame
                    keypoints = self.extract_keypoints(frame)
                    keypoints_per_frame.append(keypoints)

                    # Save the frame as an image if required
                    if saveImg:
                        frame_filename = os.path.join(self.frames_dir, f"frame_{saved_frame_count:04d}.jpg")
                        # cv2.imwrite(frame_filename, frame)
                        # saved_frame_count += 1
                        success = cv2.imwrite(frame_filename, frame)
                        if not success:
                            print(f"Failed to save image: {frame_filename}")
                        else:
                            saved_frame_count += 1

                frame_count += 1
        finally:
            self.cap.release()
        return keypoints_per_frame

    def get_total_frames(self) -> int:
        return self.total_frames

    def clear_existing_frames(self):
        if self.frames_dir and os.path.exists(self.frames_dir):
            for filename in os.listdir(self.frames_dir):
                path = os.path.join(self.frames_dir, filename)
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                except Exception as e:
                    print(f"Error deleting {path}: {e}")

    def set_frame_interval(self, frame_interval:int):
        self.frame_interval = frame_interval

    def set_frames_dir(self, frames_dir:str):
        self.frames_dir = frames_dir


# # Test
# if __name__ == "__main__":
#     video_path = r'..\data\videos\test1.mp4'
#     frames_dir = r'..\data\frame_img'  # Directory to save frames
#     frame_interval = 5  # Extract every 5th frame
#     max_frames = 100  # Optionally limit the number of frames to process
#
#     # Initialize the extractor
#     extractor = KeypointExtractor(video_path, frame_interval, max_frames, frames_dir)
#
#     # Extract keypoints and frames (frames will be saved in the specified directory)
#     keypoints_per_frame = extractor.extract_keypoints_from_video()
#
#     # Print the keypoints for the first few frames
#     print(f"Total frames: {extractor.get_total_frames()}")
#     for i, keypoints in enumerate(keypoints_per_frame[:5]):  # Print first 5 frames' keypoints
#         print(f"Frame {i + 1}: {keypoints}")
