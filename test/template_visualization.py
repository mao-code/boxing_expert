from src.template_visualizer import KeypointVisualizer
import json
from src.normalization import normalize_keypoints

if __name__ == "__main__":
    template_path = "data/templates/hook.json"
    visualizer = KeypointVisualizer()
    with open(template_path, 'r') as f:
        template = json.load(f)
        keypoints = template["keypoints"]
        normalized_template = normalize_keypoints(keypoints)

        # Plot the keypoints
        visualizer.plot_keypoints(normalized_template)

#  python -m test.template_visualization
