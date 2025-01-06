import json
import matplotlib.pyplot as plt

class KeypointVisualizer():
    def __init__(self):
        # Define connections (pairs of keypoints) for a skeleton
        self.CONNECTIONS = [
            # Face
            ("nose", "left_eye_inner"), ("left_eye_inner", "left_eye"), ("left_eye", "left_eye_outer"),
            ("nose", "right_eye_inner"), ("right_eye_inner", "right_eye"), ("right_eye", "right_eye_outer"),
            ("nose", "mouth_left"), ("nose", "mouth_right"), ("mouth_left", "mouth_right"),
            
            # Upper body
            ("left_shoulder", "right_shoulder"),
            ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
            ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
            
            # Hands (just connecting wrist to indices/pinky/thumb as an example)
            ("left_wrist", "left_index"), ("left_wrist", "left_pinky"), ("left_wrist", "left_thumb"),
            ("right_wrist", "right_index"), ("right_wrist", "right_pinky"), ("right_wrist", "right_thumb"),
            
            # Lower body
            ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"),
            ("left_hip", "right_hip"),
            ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
            ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
            ("left_ankle", "left_heel"), ("right_ankle", "right_heel"),
            ("left_heel", "left_foot_index"), ("right_heel", "right_foot_index"),
        ]

    def plot_keypoints(self, keypoints, ax=None):
        x_coords = []
        y_coords = []
        labels = []

        for kp_name, (x, y) in keypoints.items():
            x_coords.append(x)
            y_coords.append(y)
            labels.append(kp_name)

        # 3. Plot the keypoints in a scatter plot
        plt.figure(figsize=(6, 6))
        plt.scatter(x_coords, y_coords, color='red')

        # Optionally annotate each keypoint
        for i, label in enumerate(labels):
            plt.annotate(label, (x_coords[i], y_coords[i]), textcoords="offset points", xytext=(5, 5))


        # 4. Draw lines between connected keypoints
        for (start, end) in self.CONNECTIONS:
            if start in keypoints and end in keypoints:
                x_start, y_start = keypoints[start]
                x_end, y_end = keypoints[end]
                plt.plot([x_start, x_end], [y_start, y_end], color='blue')

        # Flip the y-axis for a typical image coordinate system
        plt.gca().invert_yaxis()

        plt.title("Visualization of Keypoints with Skeleton Connections")
        plt.xlabel("X coordinate")
        plt.ylabel("Y coordinate (inverted)")
        plt.axis('equal')  # Keep the aspect ratio square
        plt.grid(True)
        plt.show()

    def plot_template(self, template_path):
        with open(template_path, 'r') as f:
            template = json.load(f)

            # Plot the keypoints
            self.plot_keypoints(template["keypoints"])



