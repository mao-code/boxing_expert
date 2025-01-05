from src.keypoint_extractor import KeypointExtractor, extract_keypoints
from src.keypoint_templates import TemplateManager
from src.pose_matching import PoseMatcher


def analyze_all(video_path, template_path, frame_interval=1, max_frame=1000, threshold=0.5, frames_path=None):
    """
    Args:
        video_path:
        template_path:
        frame_interval:
        max_frame:
        threshold:
        frames_path:

    Returns:

    """
    # Initialization
    extractor = KeypointExtractor(video_path, frame_interval, max_frame, frames_path)
    # Analyze
    kps_frames = extractor.extract_keypoints_from_video()
    # Load templates
    template_manager = TemplateManager()
    template_manager.load_templates(template_path)

    # Compare keypoints to templates and match poses
    pose_matcher = PoseMatcher(threshold=threshold)  # Set the matching threshold

    kps = {}
    for frame_idx, keypoints in enumerate(kps_frames):
        best_match_name, min_distance = pose_matcher.match_pose(keypoints, template_manager.templates)
        if best_match_name:
            kps[frame_idx + 1] = best_match_name.upper()
            if frame_idx > 0 and kps[frame_idx + 1] == kps[frame_idx]:  # 上一frame和此frame技術一樣。把上一frame改小寫
                kps[frame_idx] = kps[frame_idx].lower()
        else:
            kps[frame_idx + 1] = None

    # results2show = []
    # '''
    # {'tech':"",
    # 'order': 1(last one) / 0
    # }
    # '''
    # for key, bestMatch in kps.items():
    #     if bestMatch:  # 有 tech
    #         if key < len(kps) and bestMatch == kps[key + 1]:
    #             new = {'tech': bestMatch.upper(), 'order': 0}
    #         else:  # last one
    #             new = {'tech': bestMatch.upper(), 'order': 1}
    #     else:
    #         new = {'tech': bestMatch, 'order': 0}
    #     results2show.append(new)
    return kps


def analyze_one_frame(keypoints, template_path, threshold=0.5):

    # Load templates
    template_manager = TemplateManager()
    template_manager.load_templates(template_path)

    # Compare keypoints to templates and match poses
    pose_matcher = PoseMatcher(threshold=threshold)  # Set the matching threshold
    best_match_name, min_distance = pose_matcher.match_pose(keypoints, template_manager.templates)
    if best_match_name:
        return best_match_name.upper()
    return best_match_name