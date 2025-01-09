import cv2
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QFileDialog, QCheckBox, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget,
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
import gc
import os
import mediapipe as mp
from src.analyzer import analyze_all, analyze_one_frame
from src.practice_ui import PracticeWindow

class BoxingApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.video_file_name = "None"  # 初始化 video_file_name
        self.initUI()

        # Video and analysis variables
        self.cap = None
        self.video_path = os.path.abspath(r'data/videos/test1.mp4')
        self.template_path = os.path.abspath(r'data/templates')
        self.frame_count = 0
        self.interval = 10
        self.max_frame = 1000
        self.threshold = 0.3
        self.save_frames_path = os.path.abspath(r'data/frames_img')
        self.results = {}
        self.techniques = {'HOOK': 0, 'JAB': 0, 'CROSS': 0, 'UPPERCUT': 0}
        self.tech_color = {'HOOK': 'black', 'JAB': 'black', 'CROSS': 'black', 'UPPERCUT': 'black'}
        self.changable = True
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.realTime_mode = False

    def initUI(self):
        self.setWindowTitle('Boxing Analyzer')
        self.setGeometry(100, 100, 800, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 100)  # 消除外部邊距
        main_layout.setSpacing(20)  # 控制內部元素間的間距

        # Upload layout (above video)
        upload_layout = QHBoxLayout()
        self.upload_btn = QPushButton('Upload', self)
        self.upload_btn.setFixedHeight(40)  # 強制限制高度
        self.file_label = QLabel(f"File: {self.video_file_name}", self)
        self.file_label.setStyleSheet("font-size: 20px;")  # 與按鈕文字大小一致
        self.file_label.setFixedHeight(40)  # 確保高度與按鈕一致
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addWidget(self.file_label)
        upload_layout.setSpacing(10)  # 設定按鈕與檔名之間的間距
        upload_layout.setContentsMargins(10, 0, 10, 0)  # 保持小邊距

        # Video display
        video_layout = QHBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(0)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.video_label.setScaledContents(True)
        # self.video_label.setMaximumSize(700, 700)

        # Skeleton video display layout (processed video with skeleton)
        self.skeleton_video_label = QLabel(self)
        self.skeleton_video_label.setAlignment(Qt.AlignCenter)
        self.skeleton_video_label.setStyleSheet("background-color: black;")
        self.skeleton_video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.skeleton_video_label.setScaledContents(True)
        # self.skeleton_video_label.setMaximumSize(700, 700)

        video_layout.addWidget(self.video_label)
        video_layout.addWidget(self.skeleton_video_label)

        # Technique selection layout
        technique_layout = QVBoxLayout()
        self.hook_cb = QCheckBox('Hook - 0 times', self)
        self.jab_cb = QCheckBox('Jab - 0 times', self)
        self.cross_cb = QCheckBox('Cross - 0 times', self)
        self.uppercut_cb = QCheckBox('Uppercut - 0 times', self)
        self.hook_cb.setStyleSheet("font-size: 20px;")
        self.jab_cb.setStyleSheet("font-size: 20px;")
        self.cross_cb.setStyleSheet("font-size: 20px;")
        self.uppercut_cb.setStyleSheet("font-size: 20px;")
        technique_layout.addWidget(self.hook_cb)
        technique_layout.addWidget(self.jab_cb)
        technique_layout.addWidget(self.cross_cb)
        technique_layout.addWidget(self.uppercut_cb)

        self.practice_btn = QPushButton('Practice', self)
        technique_layout.addWidget(self.practice_btn)

        # Bottom layout for play and pause buttons
        play_pause_layout = QHBoxLayout()
        self.play_btn = QPushButton('Play', self)
        self.play_btn.setFixedHeight(40)  # 強制限制高度
        self.pause_btn = QPushButton('Pause', self)
        self.pause_btn.setFixedHeight(40)  # 強制限制高度
        play_pause_layout.addWidget(self.play_btn)
        play_pause_layout.addWidget(self.pause_btn)
        play_pause_layout.setSpacing(10)

        # Main grid layout
        grid_layout = QGridLayout()
        grid_layout.addLayout(upload_layout, 0, 0, 1, 3)  # Upload above video, spanning 3 columns
        # grid_layout.addWidget(self.video_label, 1, 0, 1, 3)  # Video occupies 3 columns
        grid_layout.addLayout(technique_layout, 1, 3, 1, 1)  # Techniques on the right
        grid_layout.addLayout(play_pause_layout, 2, 0, 1, 3)  # Buttons below video, spanning 3 columns
        # Add skeleton video to the grid layout next to the original video
        # grid_layout.addWidget(self.video_label, 1, 0, 1, 2)  # The original video spans 2 columns
        # grid_layout.addWidget(self.skeleton_video_label, 1, 2, 1, 1)  # The skeleton video is on the right
        grid_layout.addLayout(video_layout, 1, 0, 1, 3)

        # Adjust row and column stretch
        grid_layout.setRowStretch(0, 1)  # Upload row (1 unit of space)
        grid_layout.setRowStretch(1, 15)  # Video row (15 units of space, majority)
        grid_layout.setRowStretch(2, 1)  # Buttons row (1 unit of space)
        grid_layout.setColumnStretch(0, 1)  # Video column (expands)
        grid_layout.setColumnStretch(1, 1)  # Video column (expands)
        grid_layout.setColumnStretch(2, 1)  # Video column (expands)
        grid_layout.setColumnStretch(3, 1)  # Technique column (also expands)

        # Add grid layout to main layout
        main_layout.addLayout(grid_layout)

        # Connect signals
        self.upload_btn.clicked.connect(self.upload_video)
        self.play_btn.clicked.connect(self.play_video)
        self.pause_btn.clicked.connect(self.pause_video)
        self.practice_btn.clicked.connect(self.open_practice_page)

        # Timer for video playback
        self.timer.timeout.connect(self.next_frame)

    def upload_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, 'Upload Video', '', 'Videos (*.mp4 *.avi)')
        if video_path:
            self.update_technique_labels()
            self.video_file_name = video_path.split("/")[-1]
        else:
            video_path = self.video_path
            self.video_file_name = "test1"

        # print(type(video_path), type(self.template_path))
        # print(video_path)
        # print(self.template_path)
        #
        # try:
        #     self.results = analyze_all(video_path, self.template_path, self.interval, self.max_frame, self.threshold)
        # except Exception as e:
        #     print(f"Error analyzing all: {e}")

        self.cap = cv2.VideoCapture(video_path)
        self.frame_count = 0
        self.techniques = {'HOOK': 0, 'JAB': 0, 'CROSS': 0, 'UPPERCUT': 0}
        self.file_label.setText(f"File: {self.video_file_name}")

    def play_video(self):
        if self.cap:
            self.timer.start(30)

    def pause_video(self):
        self.timer.stop()
        print(self.results)

    def next_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Process frame using Mediapipe Pose to get skeleton
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                kps = self.pose.process(image_rgb)

                if self.frame_count % self.interval == 0:
                    # Analyze frame
                    keypoints = {}
                    if kps.pose_landmarks:
                        for idx, landmark in enumerate(kps.pose_landmarks.landmark):
                            landmark_name = self.mp_pose.PoseLandmark(idx).name.lower()
                            keypoints[landmark_name] = [landmark.x, landmark.y]
                    self.analyze_frame(keypoints)

                self.display_frame(frame)
                self.display_skeleton_frame(frame, kps)
                self.frame_count += 1
            else:
                self.timer.stop()

    def analyze_frame(self, keypoints):
        # display
        frameNum = (self.frame_count // self.interval) + 1 # 當前的frame

        if self.realTime_mode: # 一張一張 match
            # analyze_one_frame and add to results
            self.results[frameNum] = analyze_one_frame(keypoints, self.template_path, self.threshold)

            update_text = self.results[frameNum].upper() if frameNum > 1 and self.results[frameNum] else None
            last_text = self.results[frameNum - 1].upper() if frameNum>1 and self.results[frameNum - 1] else None

            if update_text: # 有 match
                self.tech_color[update_text] = 'red'
                self.techniques[update_text] += 1

                if last_text:
                    if frameNum > 1:
                        # 不是第一個也不是最後一個
                        if last_text == update_text:  # 上一 frame 和此 frame技術一樣。把上一 frame 改小寫
                            self.techniques[update_text] -= 1
                        else: # 上一個 是連續的最後 lo
                            self.tech_color[last_text] = 'black'

                self.update_technique_labels()

            else: # 沒有match
                if last_text: # 上一個 是連續的最後
                    self.tech_color[last_text] = 'black'
                    self.update_technique_labels()

        # 先跑完整部影片的分析存在 results 裡了，這邊只處理顯示
        else:
            if self.results[frameNum]:
                update_text = self.results[frameNum].upper()
                self.tech_color[update_text] = 'red'
                if self.changable:  # 改數字
                    self.techniques[update_text] += 1
                    self.changable = False
                    self.update_technique_labels()
                if self.results[frameNum].isupper():  # 最後一次
                    self.tech_color[update_text] = 'black'
                    self.changable = True

    def display_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        if self.video_label.styleSheet() == "background-color: black;":
            self.video_label.setStyleSheet("")  # 移除背景樣式

        pixmap = QPixmap.fromImage(qimg)
        # Scale the pixmap so that it:
        #   1) Fits within the label's current size
        #   2) Preserves the aspect ratio
        #   3) Looks smooth
        target_size = self.video_label.size()  # current size of the QLabel
        scaled_pixmap = pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.video_label.setPixmap(scaled_pixmap)

    def update_technique_labels(self):
        self.hook_cb.setText(f'Hook - {self.techniques["HOOK"]} times')
        self.jab_cb.setText(f'Jab - {self.techniques["JAB"]} times')
        self.cross_cb.setText(f'Cross - {self.techniques["CROSS"]} times')
        self.uppercut_cb.setText(f'Uppercut - {self.techniques["UPPERCUT"]} times')

        self.hook_cb.setStyleSheet(f"color: {self.tech_color['HOOK']}; font-size: 20px;")
        self.jab_cb.setStyleSheet(f"color: {self.tech_color['JAB']}; font-size: 20px;")
        self.cross_cb.setStyleSheet(f"color: {self.tech_color['CROSS']}; font-size: 20px;")
        self.uppercut_cb.setStyleSheet(f"color: {self.tech_color['UPPERCUT']}; font-size: 20px;")

    def open_practice_page(self):
        """Switch to Practice Mode and open a new window for the camera."""
        self.timer.stop()  # Stop the main video playback timer if it's running

        # Gather which checkboxes are checked
        selected_techniques = []
        if self.hook_cb.isChecked():
            selected_techniques.append("HOOK")
        if self.jab_cb.isChecked():
            selected_techniques.append("JAB")
        if self.cross_cb.isChecked():
            selected_techniques.append("CROSS")
        if self.uppercut_cb.isChecked():
            selected_techniques.append("UPPERCUT")

        # Create and show the PracticeWindow
        # (Here we reuse the same template_path and threshold you used in the main window)
        self.practice_window = PracticeWindow(
            selected_techniques=selected_techniques,
            template_path=self.template_path,
            threshold=self.threshold
        )
        self.practice_window.show()

    def cleanup_camera_thread(self):
        """Ensure the camera thread stops properly."""
        if hasattr(self, 'camera_thread') and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread.wait()

    def set_results(self, result2show):
        self.results = result2show

    def set_interval(self, interval):
        self.interval = interval

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        if self.cap_camera:
            self.cap_camera.release()
        self.pose.close()
        gc.collect()
        event.accept()

    def display_skeleton_frame(self, frame, kps):
        # Draw the skeleton on the frame if pose landmarks are detected
        if kps.pose_landmarks:
            # Draw landmarks and connections
            mp.solutions.drawing_utils.draw_landmarks(frame, kps.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        # Convert the frame with skeleton to QImage for display
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        if self.skeleton_video_label.styleSheet() == "background-color: black;":
            self.skeleton_video_label.setStyleSheet("")  # 移除背景樣式

        pixmap = QPixmap.fromImage(qimg)
        # Scale the pixmap so that it:
        #   1) Fits within the label's current size
        #   2) Preserves the aspect ratio
        #   3) Looks smooth
        target_size = self.skeleton_video_label.size()  # current size of the QLabel
        scaled_pixmap = pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.skeleton_video_label.setPixmap(scaled_pixmap)

    def set_realTime_mode(self, realTime):
        self.realTime_mode = realTime

    def set_vedio_path(self, path):
        self.video_path = path


class CameraThread(QThread):
    """Thread for capturing and displaying camera frames in a new window."""
    stop_signal = pyqtSignal()  # Signal to stop the camera thread

    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None

    def run(self):
        """Main thread function to capture and display frames."""
        self.running = True
        self.cap = cv2.VideoCapture(0)  # Open the default camera

        if not self.cap.isOpened():
            print("Error: Unable to access the camera.")
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break

            # Display the frame in a new OpenCV window
            cv2.imshow("Practice Mode - Camera", frame)

            # Press 'q' to close the OpenCV window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources and close the OpenCV window
        self.cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        """Stop the thread and release the camera."""
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()
