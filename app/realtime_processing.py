import os
import cv2
import time
import threading
from queue import Queue, Empty
import streamlit as st
from pkgs.object_detection import ObjectDetector  # Replace with the actual module name
from pkgs import process_frame

def webcam_processing_thread(output_queue, merge=False, distance_threshold=50):
    """ Thread for live webcam processing to allow background frame processing """
    cap = cv2.VideoCapture(0)  # Capture from the default webcam

    if not cap.isOpened():
        output_queue.put(("error", "Error opening webcam"))
        return

    # Get the original video FPS
    original_fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Use a default of 30 FPS if the camera FPS is unknown
    frame_interval = max(1, int(original_fps / 30))  # Calculate frame skipping interval for target 30 FPS

    frame_count = 0
    last_processed_time = time.time()


    while cap.isOpened():
        try:
            ret, frame = cap.read()

            if not ret:
                break

            # Skip frames to control the FPS
            if frame_count % frame_interval == 0:
                # Process the frame if it's time
                processed_frame = process_frame(frame, merge, distance_threshold)

                # Calculate time elapsed for frame processing to display FPS
                current_time = time.time()
                time_elapsed = current_time - last_processed_time
                fps_display = 1 / time_elapsed if time_elapsed > 0 else 0
                last_processed_time = current_time

                # Send the processed frame and FPS to the output queue
                output_queue.put(("frame", processed_frame, fps_display))

            frame_count += 1
        except Exception as e:
            print("Error:", e) 
            cap.release()
            output_queue.put(("done",)) 

    cap.release()
    output_queue.put(("done",))

def live_webcam_detection(merge=False, distance_threshold=50):
    """ Handles live webcam detection using threading and displays results in Streamlit """
    output_queue = Queue()

    # Start the webcam processing in a separate thread
    webcam_thread = threading.Thread(target=webcam_processing_thread, args=(output_queue, merge, distance_threshold))
    webcam_thread.start()

    stframe = st.empty()

    # Continuously display processed frames in the Streamlit app
    while True:
        try:
            message = output_queue.get(timeout=1)

            if message[0] == "frame":
                frame, fps_display = message[1], message[2]
                stframe.image(frame, channels="BGR", caption=f"FPS: {fps_display:.2f}")
            elif message[0] == "error":
                st.error(message[1])
                break
            elif message[0] == "done":
                st.success("Webcam processing completed")
                break

        except Empty:  # Handle empty queue error
            continue