import streamlit as st 
import tempfile
from app import process_video, live_webcam_detection, display_image_processing
import os

def start_web_page(title="Live Fire Detection from Webcam, Video, Image"):
    # In your Streamlit app, you can now call `live_webcam_detection()` for live webcam object detection
    st.title(title)

    option = st.selectbox("Choose input source", ("Video File", "Webcam", "Image"))

    if option == "Video File":
        video_path = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
        if video_path is not None:
            # Create a temporary file to store the uploaded video
            tfile = tempfile.NamedTemporaryFile(delete=False)  
            tfile.write(video_path.read())
            
            # Pass the temporary file path to the process_video function
            process_video(tfile.name)
    elif option == "Webcam":
        live_webcam_detection()
    elif option == "Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        # temp_image_path = os.path.join(os.getcwd(), 'temp_uploaded_image.jpg')
        if uploaded_file is not None:
        # Save the uploaded file to a temporary location
            temp_image_path = os.path.join(os.getcwd(), 'temp_uploaded_image.jpg')
            print("Path: ", temp_image_path)
            with open(temp_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Display and process the uploaded image
            display_image_processing(temp_image_path, merge=False, distance_threshold=50)
            