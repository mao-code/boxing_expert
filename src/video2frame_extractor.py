import shutil
import cv2
import os

class VideoFrameExtractor:
    def __init__(self, video_path:str, frames_dir:str, frame_interval: int = 1, max_frames: int = None):
        self.video_path = video_path
        self.output_dir = frames_dir
        self.frame_interval = frame_interval
        self.max_frames = max_frames
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Error: Couldn't open video {self.video_path}")

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def extract_frames(self):
        '''
        extract frames and store in file named 'output_dir'
        '''
        frame_count = 0
        saved_frame_count = 0

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        while True:
            if self.max_frames and frame_count >= self.max_frames:
                break
            ret, frame = self.cap.read()
            if not ret:
                break

            if frame_count % self.frame_interval == 0:
                frame_filename = os.path.join(self.output_dir, f"frame_{saved_frame_count:04d}.jpg")
                cv2.imwrite(frame_filename, frame)
                saved_frame_count += 1

        self.cap.release()

    def get_total_frames(self) -> int:
        return self.total_frames

    def set_frame_interval(self, frame_interval:int):
        self.frame_interval = frame_interval

    def clear_existing_frames(self):
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                path = os.path.join(self.output_dir, filename)
                try:
                    if os.path.isfile((path)):
                        os.remove((path))
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                except Exception as e:
                    print(f"Error deleting {path}: {e}")
