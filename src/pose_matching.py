import numpy as np
from typing import Dict, Tuple
from src.normalization import normalize_keypoints

class PoseMatcher:
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold  # Threshold for considering a pose as matched

    def compute_distance(self, keypoints_a: Dict[str, List[float]], keypoints_b: Dict[str, List[float]], method: str = 'euclidean') -> float:
        """
        Compute the distance between two sets of keypoints.
        """
        common_keypoints = set(keypoints_a.keys()).intersection(set(keypoints_b.keys()))
        if not common_keypoints:
            return float('inf')  # No common keypoints to compare

        distances = []
        for key in common_keypoints:
            point_a = np.array(keypoints_a[key])
            point_b = np.array(keypoints_b[key])
            if method == 'euclidean':
                distances.append(np.linalg.norm(point_a - point_b))
            else:
                raise ValueError(f"Unsupported distance method: {method}")

        if not distances:
            return float('inf')

        return np.mean(distances)

    def match_pose(self, detected_keypoints: Dict[str, List[float]], templates: Dict[str, 'BoxingPoseTemplate']) -> Tuple[str, float]:
        """
        Compare the detected keypoints against all templates and return the best match.
        """
        normalized_detected = normalize_keypoints(detected_keypoints)
        min_distance = float('inf')
        best_match_name = None

        for name, template in templates.items():
            normalized_template = normalize_keypoints(template.keypoints)
            distance = self.compute_distance(normalized_detected, normalized_template)
            if distance < min_distance:
                min_distance = distance
                best_match_name = name

        if min_distance <= self.threshold:
            return best_match_name, min_distance
        else:
            return None, min_distance  # No pose matches within the threshold