import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2


class BoxingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Boxing Analyzer")
        self.video_file_name = "None"
        self.cap = None
        self.timer = None

        # to set
        self.frame_count = 0
        self.interval = 10  # Example interval
        self.updateInfo = []

        # Upload Section
        self.upload_frame = tk.Frame(root)
        self.upload_frame.pack(pady=5)
        self.upload_btn = tk.Button(self.upload_frame, text="Upload", command=self.upload_video)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        self.file_label = tk.Label(self.upload_frame, text=f"File: {self.video_file_name}")
        self.file_label.pack(side=tk.LEFT)

        # Video Display Section
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Technique Section
        self.tech_frame = tk.Frame(root)
        self.tech_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.tech_labels = ["Hook", "Jab", "Cross", "Uppercut"]
        self.tech_checkboxes = {}

        for tech in self.tech_labels:
            # Checkbutton
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self.tech_frame, text=tech, variable=var, font=("Arial", 16))
            cb.pack(anchor=tk.W)
            self.tech_checkboxes[tech] = cb

        # Practice Button
        self.practice_btn = tk.Button(self.tech_frame, text="Practice", command=self.open_practice_page)
        self.practice_btn.pack(pady=10)

        # Play/Pause Section
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=5)
        self.play_btn = tk.Button(self.control_frame, text="Play", command=self.play_video)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = tk.Button(self.control_frame, text="Pause", command=self.pause_video)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

    def upload_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
        if video_path:
            self.video_file_name = video_path.split("/")[-1]
        else:
            video_path = r'data/videos/test1.mp4'
        self.cap = cv2.VideoCapture(video_path)
        self.file_label.config(text=f"File: {self.video_file_name}")

    def play_video(self):
        if self.cap:
            self.timer = self.root.after(30, self.update_frame)

    def pause_video(self):
        if self.timer:
            self.root.after_cancel(self.timer)
            self.timer = None

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Get canvas size and resize frame
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            frame_height, frame_width, _ = frame.shape
            scale = min(canvas_width / frame_width, canvas_height / frame_height)
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Convert to ImageTk format
            image = Image.fromarray(resized_frame)
            self.tk_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.tk_image, anchor=tk.CENTER)

            # Update action highlight
            if self.frame_count % self.interval == 0:
                self.update_action_highlight()

            self.frame_count += 1

            # Continue playback
            self.timer = self.root.after(30, self.update_frame)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            self.frame_count = 0

    def update_action_highlight(self):
        current_action = self.updateInfo[self.frame_count // self.interval]
        for tech, cb in self.tech_checkboxes.items():
            if current_action and tech.upper() == current_action['tech']:
                cb.config(bg="yellow", fg="black")  # 高亮匹配的动作，背景黄色，文字黑色
            else:
                cb.config(bg='white',fg="black")  # 恢复默认背景和文字颜色

    def open_practice_page(self):
        print("Practice page opened.")

    def close(self):
        if self.cap:
            self.cap.release()

    def set_interval(self, interval):
        self.interval = interval

    def set_update_info(self, upIn):
        self.updateInfo = upIn


VIDEO_PATH = r'data/videos/test1.mp4'
FRAMES_PATH = r'data/frames_img'
FRAME_INTERVAL = 5
MAX_FRAME = 1000
TEMPLATE_PATH = r'data/templates'
THRESHOLD = 0.5


# root = tk.Tk()
# root.geometry("800x600")
# app = BoxingApp(root)
# app.set_interval(FRAME_INTERVAL)
# app.set_update_info(results2show)
# root.protocol("WM_DELETE_WINDOW", app.close)
# root.mainloop()