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

# 會上下顛倒，導致判斷結果錯誤
# def normalize_keypoints(keypoints: Dict[str, List[float]]) -> Dict[str, List[float]]:
#     """
#     Aligns the skeleton so that:
#       - The midpoint between (left_shoulder, right_shoulder) is at the origin.
#       - The line (left_shoulder -> right_shoulder) is aligned with the +X axis.
#       - The distance between shoulders is scaled to 1.
    
#     Parameters
#     ----------
#     keypoints : Dict[str, List[float]]
#         e.g., {
#            "left_shoulder": [0.3, 0.4],
#            "right_shoulder": [0.5, 0.4],
#            "left_hip": [0.31, 0.7],
#            ...
#         }
#         Each value is [x, y], in normalized [0..1] or pixel coordinates.

#     Returns
#     -------
#     aligned_keypoints : Dict[str, List[float]]
#         Pose is translated & rotated so that:
#           (left_shoulder, right_shoulder) => same y-coordinate, shoulders on X-axis
#           The midpoint of those shoulders => origin (0,0)
#           The shoulders are exactly 1 unit apart on X-axis.
#     """
#     # We need both shoulders to align
#     if "left_shoulder" not in keypoints or "right_shoulder" not in keypoints:
#         # Fallback: If we can't find them, just return as-is
#         return keypoints

#     left_shoulder = np.array(keypoints["left_shoulder"], dtype=np.float32)
#     right_shoulder = np.array(keypoints["right_shoulder"], dtype=np.float32)

#     # 1) Translate so the midpoint of the shoulders is at (0,0)
#     midpoint = (left_shoulder + right_shoulder) / 2.0

#     # Center all keypoints
#     names = list(keypoints.keys())
#     points = np.array([keypoints[n] for n in names], dtype=np.float32)
#     points_centered = points - midpoint  # shape (N, 2)

#     # 2) Rotate so the shoulder line is on the X-axis
#     #    Vector from left_shoulder to right_shoulder (after translation)
#     ls_centered = left_shoulder - midpoint
#     rs_centered = right_shoulder - midpoint
#     shoulder_vec = rs_centered - ls_centered  # shape (2,)

#     # Angle between 'shoulder_vec' and the x-axis
#     angle = np.arctan2(shoulder_vec[1], shoulder_vec[0])

#     # We'll rotate by -angle to align shoulders with +X
#     rotation_matrix = np.array([
#         [np.cos(-angle), -np.sin(-angle)],
#         [np.sin(-angle),  np.cos(-angle)]
#     ], dtype=np.float32)

#     # Apply rotation to all points
#     points_rotated = points_centered @ rotation_matrix.T  # shape (N, 2)

#     # 3) Scale so distance between shoulders is 1
#     ls_rotated = ls_centered @ rotation_matrix.T
#     rs_rotated = rs_centered @ rotation_matrix.T
#     shoulder_dist = np.linalg.norm(rs_rotated - ls_rotated)
#     if shoulder_dist > 1e-8:
#         points_rotated /= shoulder_dist

#     # Now store back into a dict
#     aligned_keypoints = {}
#     for i, name in enumerate(names):
#         aligned_keypoints[name] = points_rotated[i].tolist()

#     return aligned_keypoints
