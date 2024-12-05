import numpy as np
from typing import Dict, List

def normalize_keypoints(keypoints: Dict[str, List[float]]) -> Dict[str, List[float]]:
    """
    Normalize keypoints to have zero mean and unit variance.
    """
    points = np.array(list(keypoints.values()))
    mean = np.mean(points, axis=0)
    std = np.std(points, axis=0) + 1e-8  # Avoid division by zero

    normalized_keypoints = {}
    for key, point in keypoints.items():
        normalized_point = (np.array(point) - mean) / std
        normalized_keypoints[key] = normalized_point.tolist()

    return normalized_keypoints
