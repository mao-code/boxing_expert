import cv2
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QFileDialog, QCheckBox, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget,
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
import os
import gc


class VideoProcessorThread(QThread):
    update_frame_signal = pyqtSignal(object)  # 發送處理後的影像
    update_labels_signal = pyqtSignal(dict)  # 發送更新的技術數據
    frame_processed_signal = pyqtSignal(int, dict)  # 傳送幀和對應的結果

    def __init__(self, cap, interval, tech_color, results):
        super().__init__()
        self.cap = cap
        self.interval = interval
        self.tech_color = tech_color
        self.results = results
        self.frame_count = 0
        self.running = True  # 控制是否繼續播放

    def run(self):
        while self.cap.isOpened() and self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_count += 1

                if self.frame_count % self.interval == 0:
                    self.analyze_frame(frame)

                # 顯示處理後的影像
                self.update_frame_signal.emit(frame)

                # 每個幀處理後發送分析結果
                self.frame_processed_signal.emit(self.frame_count, self.results)

            else:
                break

    def analyze_frame(self, frame):
        # 分析當前幀，並根據結果更新技術顏色
        if self.frame_count % self.interval == 0:  # 分析每個間隔幀
            frameNum = self.frame_count // self.interval
            if frameNum in self.results and self.results[frameNum]['tech']:
                tech = self.results[frameNum]['tech'].upper()
                if tech in self.tech_color:
                    self.tech_color[tech] = 'red'
                    self.update_labels_signal.emit(self.tech_color)
                if self.results[frameNum]['order'] == 1:  # 最後一次
                    self.tech_color[tech] = 'black'
                    self.update_labels_signal.emit(self.tech_color)

    def stop(self):
        self.running = False

from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QFileDialog, QCheckBox, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
import cv2
import gc
import os

class BoxingApp(QMainWindow):
    # 定義兩個信號
    update_frame_signal = pyqtSignal(object)  # 發送處理後的影像
    update_labels_signal = pyqtSignal(dict)  # 發送更新的技術數據

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.video_file_name = "None"  # 初始化 video_file_name
        self.initUI()

        # Video and analysis variables
        self.cap = None
        self.video_path = os.path.abspath(r'data/videos/test1.mp4')
        self.frame_count = 0
        self.interval = 10
        self.results = {}
        self.changable = True

    def initUI(self):
        self.setWindowTitle('Boxing Analyzer')
        self.setGeometry(100, 100, 800, 600)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Central widget and layout
        central_widget = QWidget(self)
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 100)  # 消除外部邊距
        main_layout.setSpacing(20)  # 控制內部元素間的間距

        # Upload layout (above video)
        upload_layout = QHBoxLayout()
        self.upload_btn = QPushButton('Upload', self)
        self.upload_btn.setFixedHeight(40)  # 強制限制高度
        self.file_label = QLabel(f"File: {self.video_file_name}", self)
        self.file_label.setStyleSheet("font-size: 24px;")  # 與按鈕文字大小一致
        self.file_label.setFixedHeight(40)  # 確保高度與按鈕一致
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addWidget(self.file_label)
        upload_layout.setSpacing(10)  # 設定按鈕與檔名之間的間距
        upload_layout.setContentsMargins(10, 0, 10, 0)  # 保持小邊距

        # Video display
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Technique selection layout
        technique_layout = QVBoxLayout()
        techniques = ['Hook', 'Jab', 'Cross', 'Uppercut']
        self.tech_color = {'HOOK': 'black', 'JAB': 'black', 'CROSS': 'black', 'UPPERCUT': 'black'}
        self.technique_cbs = {}

        for technique in techniques:
            checkbox = QCheckBox(technique, self)
            object_name = technique.lower()
            checkbox.setObjectName(object_name)
            checkbox.setStyleSheet(f"color: {self.tech_color[technique.upper()]}; font-size: 40px;")
            technique_layout.addWidget(checkbox)
            self.technique_cbs[technique.upper()] = checkbox

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
        grid_layout.addWidget(self.video_label, 1, 0, 1, 3)  # Video occupies 3 columns
        grid_layout.addLayout(technique_layout, 1, 3, 1, 1)  # Techniques on the right
        grid_layout.addLayout(play_pause_layout, 2, 0, 1, 3)  # Buttons below video, spanning 3 columns

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

        # Connect update signals
        self.update_frame_signal.connect(self.display_frame)
        self.update_labels_signal.connect(self.update_technique_labels)

        # Timer for video playback
        self.timer.timeout.connect(self.next_frame)

    def upload_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, 'Upload Video', '', 'Videos (*.mp4 *.avi)')
        if video_path:
            self.update_technique_labels()
            # Update file name label
            self.video_file_name = video_path.split("/")[-1]
        else:
            # Reset to default if no file selected
            video_path = self.video_path
            self.video_file_name = "test1"
        self.cap = cv2.VideoCapture(video_path)
        self.frame_count = 0
        self.file_label.setText(f"File: {self.video_file_name}")

    def play_video(self):
        if self.cap:
            self.timer.start(30)

    def pause_video(self):
        self.timer.stop()

    def next_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frame_count += 1

                if self.frame_count % self.interval == 0:
                    # Analyze frame
                    self.analyze_frame(frame)

                self.display_frame(frame)

            else:
                self.timer.stop()

    def analyze_frame(self, frame):
        '''
            {'tech':"",
            'order': 1(last)/0
            }
        '''
        if self.frame_count % self.interval == 0:
            frameNum = self.frame_count // self.interval
            if self.results[frameNum]['tech']:
                update_text = self.results[frameNum]['tech'].upper()
                self.tech_color[update_text] = 'red'
                self.update_technique_labels()

                if self.results[frameNum]['order']:
                    self.tech_color[update_text] = 'black'

    def display_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        if self.video_label.styleSheet() == "background-color: black;":
            self.video_label.setStyleSheet("")  # 移除背景樣式

        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def update_technique_labels(self):
        for technique, color in self.tech_color.items():
            checkbox = self.technique_cbs.get(technique)
            if checkbox and checkbox.styleSheet() != f"color: {color}; font-size: 40px;":
                checkbox.setStyleSheet(f"color: {color}; font-size: 40px;")

    def open_practice_page(self):
        print("Practice page opened.")
        practice_window = QWidget()
        practice_window.setWindowTitle("Practice Page")
        practice_window.setGeometry(200, 200, 400, 300)
        practice_window.show()

    def set_results(self, result2show):
        self.results = result2show

    def set_interval(self, interval):
        self.interval = interval