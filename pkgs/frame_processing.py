import os
import cv2
import time
import threading
from queue import Queue, Empty
import streamlit as st
from pkgs.object_detection import ObjectDetector  # Replace with the actual module name

model_dir = os.path.join('model', 'inference')
detector = ObjectDetector(model_path=os.path.join(model_dir, 'fire-detection.pt'), gpu=False)

def process_frame(frame, merge: bool = False, distance_threshold: int = 50):
    """ Processes a frame with object detection, optionally merges nearby objects """
    original_shape = frame.shape[:2]  # Get original frame height and width

    # Convert frame to RGB as OpenCV works in BGR
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Perform object detection using the detector class
    resized_frame, detections = detector.detect_objects(frame_rgb)

    if merge:
        detections = detector.merge_obj(detections, distance_threshold=distance_threshold)

    # Rescale the bounding boxes back to the original frame size if needed
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        
        # Rescale bbox coordinates to original image size
        x1 = int(x1 * (original_shape[1] / 640))  # Width scale
        y1 = int(y1 * (original_shape[0] / 640))  # Height scale
        x2 = int(x2 * (original_shape[1] / 640))  # Width scale
        y2 = int(y2 * (original_shape[0] / 640))  # Height scale

        label = f"{det['label']} {det['score']:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return frame