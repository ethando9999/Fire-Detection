import os
import cv2
import time
import threading
from queue import Queue, Empty
import streamlit as st
from pkgs import process_frame

def video_processing_thread(video_path, output_queue, merge=False, distance_threshold=50):
    """ Thread for video file processing to allow background frame processing """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        output_queue.put(("error", "Error opening video file"))
        return

    frame_count = 0
    last_processed_time = time.time()
    
    try:
        while cap.isOpened():
        
                ret, frame = cap.read()

                if not ret:
                    break

                # Process the frame
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

def process_video(video_path, merge=False, distance_threshold=50):
    """ Handles the video processing using threading and displays results in Streamlit """
    output_queue = Queue()
    
    # Start the video processing in a separate thread
    video_thread = threading.Thread(target=video_processing_thread, args=(video_path, output_queue, merge, distance_threshold))
    video_thread.start()

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
                st.success("Video processing completed")
                break

        except Empty:  # Handle empty queue error
            continue
