import os
import cv2
import time
import threading
from queue import Queue, Empty
import streamlit as st
from pkgs import object_detection, process_frame, detector

def process_image(image_path, merge=False, distance_threshold=50):
    """
    Reads and processes a single image for object detection.
    Optionally merges nearby detected objects.
    
    Args:
        image_path (str): Path to the input image.
        merge (bool): Whether to merge nearby objects.
        distance_threshold (int): Distance threshold for merging objects.
        
    Returns:
        processed_image: Image with bounding boxes and labels drawn on it.
    """
    # Read the image from the given path
    frame = cv2.imread(image_path)

    if frame is None:
        st.error(f"Error loading image from {image_path}")
        return None

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


def display_image_processing(image_path, merge=False, distance_threshold=50):
    """ Handles processing and displaying the image in Streamlit """
    processed_image = process_image(image_path, merge, distance_threshold)

    if processed_image is not None:
        st.image(processed_image, channels="BGR", caption="Processed Image with Object Detection")