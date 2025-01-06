import random
import cv2
import mediapipe as mp
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QSizePolicy

from src.analyzer import analyze_one_frame

class PracticeWindow(QMainWindow):
    """
    A window that shows live camera feed, a randomly placed target,
    and a score for hitting the target with the correct technique.
    """
    def __init__(self, selected_techniques=None, template_path=None, threshold=0.5, parent=None):
        super().__init__(parent)
        self.technique_hand_map = {
            "CROSS": "right_wrist",
            "UPPERCUT": "right_wrist",
            "JAB": "left_wrist",
            "HOOK": "left_wrist"
        }

        self.setWindowTitle("Practice Mode")
        self.setGeometry(200, 100, 600, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Pose model init
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

        # Keep references to user preferences
        self.selected_techniques = selected_techniques or []  # e.g. ["HOOK", "JAB"]
        self.template_path = template_path
        self.threshold = threshold

        # Score initialization
        self.score = 0

        # Random target parameters (x, y, radius)
        self.target_x = 1176
        self.target_y = 372
        self.target_radius = 150

        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Score label
        self.score_label = QLabel("Score: 0", self)
        self.score_label.setStyleSheet("font-size: 24px; color: green;")
        layout.addWidget(self.score_label, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.score_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Video/camera feed label
        self.camera_label = QLabel(self)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("background-color: black;")
        layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setScaledContents(True)
        self.camera_label.setMaximumSize(1920, 1080)

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Warning: Unable to access camera. Check if another application is using it.")

        # Timer for retrieving camera frames and updating UI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(30)  # about 30 FPS

        # Another timer (optional) for moving the target to a new random position periodically
        # e.g., every 3 seconds
        self.move_target_timer = QTimer(self)
        self.move_target_timer.timeout.connect(self.randomize_target_position)
        self.move_target_timer.start(3000)

    def randomize_target_position(self):
        """Randomly relocate the target within the camera frame."""
        frame_w, frame_h = 1500, 1000 # default values
        max_x = frame_w - 2 * self.target_radius
        max_y = frame_h - 2 * self.target_radius - 200
        if max_x < 0 or max_y < 0:
            return
        
        self.target_x = random.randint(max_x-100, max_x+100)
        self.target_y = random.randint(self.target_radius+100, max_y)

    def next_frame(self):
        """Captures a camera frame, processes it, draws the target, and checks for hits."""
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # Mirror the frame
        # frame = cv2.flip(frame, 1)

        # Convert to RGB for Mediapipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Run pose detection
        keypoints_result = self.pose.process(image_rgb)

        # 1) Draw the target on the frame

        # 2) Check if user hits target with the correct technique
        if keypoints_result.pose_landmarks:
            # Convert mediapipe landmarks into a dictionary {landmark_name: [x, y]}
            keypoints = {}
            for idx, landmark in enumerate(keypoints_result.pose_landmarks.landmark):
                name = self.mp_pose.PoseLandmark(idx).name.lower()
                keypoints[name] = [landmark.x, landmark.y]  # normalized coords [0,1]

            # ----- Check for technique correctness -----
            recognized_tech = analyze_one_frame(keypoints, self.template_path, self.threshold)
            recognized_tech = recognized_tech.upper() if recognized_tech else None 

            # If recognized technique is one of the user-selected techniques, proceed to check "hit"
            if recognized_tech in self.selected_techniques:
                # Pass recognized_tech to is_hit
                if self.is_hit(recognized_tech, keypoints, frame):
                    self.score += 1
                    self.score_label.setText(f"Score: {self.score}")
                    self.randomize_target_position()


        # 3) Convert the frame to QPixmap and draw the target with QPainter
        #    Because the frame is BGR from OpenCV, convert to RGB

        # Draw the skeleton on the frame if pose landmarks are detected
        if keypoints_result.pose_landmarks:
            # Draw landmarks and connections
            mp.solutions.drawing_utils.draw_landmarks(frame, keypoints_result.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        if self.camera_label.styleSheet() == "background-color: black;":
            self.camera_label.setStyleSheet("")  

        # Draw the target using QPainter
        painter = QPainter()
        pixmap = QPixmap.fromImage(qimg)
        painter.begin(pixmap)
        pen = QPen(QColor("red"))
        pen.setWidth(4)
        painter.setPen(pen)
        painter.setBrush(QColor(255, 0, 0, 128))  # semi-transparent red
        painter.drawEllipse(self.target_x, self.target_y, self.target_radius, self.target_radius)
        painter.end()

        # 4) Display on camera_label
        self.camera_label.setPixmap(pixmap)

    def is_hit(self, recognized_tech, keypoints, frame):
        """
        Checks if the user hits the target using the correct hand for the recognized technique.
        """

        if recognized_tech not in self.technique_hand_map:
            # If the technique wasn't mapped, default to 'right_wrist' or return False
            return False

        required_hand = self.technique_hand_map[recognized_tech]

        # 2. Verify the keypoints have that hand
        if required_hand not in keypoints:
            return False

        # 3. Convert normalized [0..1] coordinates to the frame size
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_h, frame_w, ch = frame_rgb.shape
        # frame_w, frame_h = 1500, 1000 # default values
        rx_norm, ry_norm = keypoints[required_hand]

        hand_x = int(rx_norm * frame_w)
        hand_y = int(ry_norm * frame_h)

        # print("INFO: Recognized technique:", recognized_tech)
        # print("INFO: Hand location:", hand_x, hand_y)
        # print("INFO: Target location:", self.target_x, self.target_y)

        # 4. Check if that hand location lies within the target circle
        dist_sq = (hand_x - self.target_x) ** 2 + (hand_y - self.target_y) ** 2
        radius_sq = self.target_radius ** 2
        # If within circle => "hit"
        return dist_sq <= radius_sq


    def closeEvent(self, event):
        """Cleanup resources when window is closed."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.pose.close()
        super().closeEvent(event)
