import os
import json
from typing import Dict, List

class BoxingPoseTemplate:
    def __init__(self, name: str, keypoints: Dict[str, List[float]]):
        self.name = name
        self.keypoints = keypoints  # keypoints as a dictionary {landmark_name: [x, y]}

    @classmethod
    def from_file(cls, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls(name=data['name'], keypoints=data['keypoints'])

    def to_file(self, file_path: str):
        data = {
            'name': self.name,
            'keypoints': self.keypoints
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

class TemplateManager:
    def __init__(self):
        self.templates = {}  # Dict[str, BoxingPoseTemplate]

    def load_templates(self, directory: str):
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                template = BoxingPoseTemplate.from_file(file_path)
                self.templates[template.name] = template

    def get_template(self, name: str) -> BoxingPoseTemplate:
        return self.templates.get(name)
