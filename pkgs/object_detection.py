import os
import cv2
import numpy as np
import torch
from ultralytics import RTDETR, YOLO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ObjectDetector class for detection and merging logic
class ObjectDetector:
    def __init__(self, model_path=None, gpu=True):
        gpu_available = torch.cuda.is_available() if gpu else False
        self.device = 'cuda' if gpu_available else 'cpu'
        # self.model = RTDETR(model_path or os.path.join(os.getcwd(), 'rt_detr_trash_cls_1.pt')).to(self.device) # Using rt-detr for trash cls
        self.model = YOLO(model_path or os.path.join('fire-detection.pt')).to(self.device) # Change model yolo detect garbage bag when needed.
    def detect_objects(self, image, conf_threshold=0.2):
        image_resized = cv2.resize(image, (640, 640))
        image_tensor = torch.from_numpy(image_resized).float().permute(2, 0, 1).unsqueeze(0).to(self.device)
        image_tensor /= 255.0
        results = self.model.predict(image_tensor, conf=conf_threshold)
        # results = self.model.predict(image, conf=conf_threshold)
        detections = []
        # Process detection results and filter out low confidence detections
        if results and hasattr(results[0], 'boxes') and results[0].boxes is not None:
            boxes_data = results[0].boxes.data
            if len(boxes_data) > 0:
                for result in boxes_data:
                    detections.append({
                        'bbox': [int(coord) for coord in result[:4].tolist()],
                        'score': float(result[4]),
                        'class': int(result[5]),
                        'label': self.model.names[int(result[5])]
                    })
        return image_resized, detections

    def merge_obj(self, obj_positions, distance_threshold=50):
        if not obj_positions:
            return []

        def get_centroid(bbox):
            x1, y1, x2, y2 = bbox
            return [(x1 + x2) / 2, (y1 + y2) / 2]

        def euclidean_distance(pt1, pt2):
            return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5

        merged_positions = []

        while obj_positions:
            base_obj = obj_positions.pop(0)
            base_bbox = base_obj['bbox']
            base_centroid = get_centroid(base_bbox)
            nearby_objects = [base_obj]

            for other_obj in obj_positions[:]:
                other_bbox = other_obj['bbox']
                other_centroid = get_centroid(other_bbox)
                distance = euclidean_distance(base_centroid, other_centroid)

                if distance < distance_threshold:
                    nearby_objects.append(other_obj)
                    obj_positions.remove(other_obj)

            if len(nearby_objects) > 1:
                x_min = min(obj['bbox'][0] for obj in nearby_objects)
                y_min = min(obj['bbox'][1] for obj in nearby_objects)
                x_max = max(obj['bbox'][2] for obj in nearby_objects)
                y_max = max(obj['bbox'][3] for obj in nearby_objects)

                merged_confidence = np.mean([obj['score'] for obj in nearby_objects])
                merged_label = ' & '.join(set(obj['label'] for obj in nearby_objects))

                merged_positions.append({
                    'bbox': [x_min, y_min, x_max, y_max],
                    'score': merged_confidence,
                    'class': base_obj['class'],
                    'label': merged_label
                })
            else:
                merged_positions.append(base_obj)

        return merged_positions

