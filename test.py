from src.keypoint_extractor import KeypointExtractor
from src.keypoint_templates import TemplateManager
from src.pose_matching import PoseMatcher
import sys
from PyQt5.QtWidgets import QApplication
from src.UI import BoxingApp
# from src.UI_tk import BoxingApp
from src.analyzer import analyze_all, analyze_one_frame

VIDEO_PATH = r'data/videos/test1.mp4'
FRAMES_PATH = r'data/frames_img'
FRAME_INTERVAL = 10
MAX_FRAME = 1000
TEMPLATE_PATH = r'data/templates'
THRESHOLD = 0.5


def main():

    results = analyze_all(VIDEO_PATH, TEMPLATE_PATH, FRAME_INTERVAL, MAX_FRAME, THRESHOLD, FRAMES_PATH)
    # print(results)

    app = QApplication(sys.argv)
    mainWin = BoxingApp()

    mainWin.set_results(results)
    # mainWin.set_realTime_mode(True)

    mainWin.set_interval(FRAME_INTERVAL)
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
