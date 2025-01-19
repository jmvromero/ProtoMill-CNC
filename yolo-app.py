import streamlit as st
import cv2
from PIL import Image
import numpy as np
from streamlit_cropper import st_cropper
from ultralytics import YOLO
from smbus2 import SMBus
from RPLCD.i2c import CharLCD  # Library for I2C LCD communication

# Setup the I2C LCD with appropriate I2C address and port
bus = SMBus(1)  # Use I2C bus 1 (on Raspberry Pi)
lcd_address = 0x27  # Replace with your LCD's I2C address
lcd = CharLCD('PCF8574', lcd_address, auto_linebreaks=True)


# Function to initialize LCD display
def setup_lcd():
    try:
        lcd.clear()  # Clear any existing message on the LCD
        lcd.write_string("ProtoMill CNC\nInitializing...")
    except Exception as e:
        print(f"Error initializing LCD: {e}")


model= YOLO(r"C:\Users\JULIA-ANN\PycharmProjects\ProtoMill-CNC\train3\weights\best.pt")


# Home Page (Overview & Introduction)
def home_page():
    # Set the title and introductory text
    st.title("InspectMill")
    st.write("""
    Welcome to the InspectMill, a PCB Defect Detection Tool powered by OpenCV and Streamlit. This tool helps you to detect defects in your PCB designs by comparing a template PCB image with an output image from your CNC machine.
    """)

    st.write("""
    ### Instructions:
    1. **Capture the Output Image**:Capture the PCB output image from your CNC machine.
    2. **Detection from Yolo-V8**: The app will use the model to detect the defects.
    3. **Results**: View the detected defects and download the results.
    """)

    # Next Button to go to the Template Image Upload page
    next_button = st.button("Next")
    if next_button:
        st.session_state.page = "capture_output_image"  # Go to Capture Output Image PAge
        st.rerun()  # Use st.rerun() instead of deprecated experimental_rerun

def capture_output_image_page():
    st.title("Capture or Detect PCB Defects")

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

    mode = st.radio("Choose a mode:", ["Real-Time Detection", "Capture/Upload Image"])

    if mode == "Real-Time Detection":
        st.subheader("Real-Time YOLOv8 PCB Defect Detection")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Unable to access the webcam.")
            return

        FRAME_WINDOW = st.image([])

        frame_count = 0
        skip_frames = 3  # Process every third frame

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.warning("Unable to capture a frame from the webcam.")
                break

            frame_count += 1
            if frame_count % skip_frames != 0:
                continue  # Skip frames to reduce workload

            # Resize frame to reduce processing time
            resized_frame = cv2.resize(frame, (640, 480))

            # Pass the resized frame to YOLO
            yolo_results = model.predict(source=resized_frame, save=False, conf=0.25)

            # Annotate the frame with detection results
            annotated_frame = yolo_results[0].plot()

            # Resize the annotated frame for Streamlit rendering
            annotated_frame = cv2.resize(annotated_frame, (640, 480))  # Lower resolution for UI

            # Update the live feed
            FRAME_WINDOW.image(annotated_frame, channels="BGR", use_container_width=True)

        cap.release()
        cv2.destroyAllWindows()

    elif mode == "Capture/Upload Image":
        st.subheader("Capture or Upload PCB Output Image")

        # Camera input for image capture
        st.subheader("Capture Image from Camera")
        camera_image = st.camera_input("Capture Output Image from Camera")

        # File uploader for image uploading
        st.subheader("Or Upload an Image")
        uploaded_image = st.file_uploader("Upload your output image (e.g., PNG, JPG, JPEG):",
                                          type=["png", "jpg", "jpeg"])

        # Check if camera image or uploaded image is provided
        if camera_image or uploaded_image or "captured_frame" in st.session_state:
            st.subheader("Selected PCB Image")

            if camera_image:
                # Use the camera-captured image
                image = Image.open(camera_image)
                st.write("Image captured using the camera.")
            elif uploaded_image:
                # Use the uploaded image
                image = Image.open(uploaded_image)
                st.write("Image uploaded successfully.")
            else:
                # Use the previously captured frame from real-time detection
                image = st.session_state.captured_frame
                st.write("Using the captured frame from Real-Time Detection.")

            # Display the image
            st.image(image, caption="Selected Image", use_container_width=True)

            # Save the selected image to session state
            st.session_state.output_img = image

            # Cropping functionality
            st.subheader("Crop the Image")
            cropped_image = st_cropper(
                st.session_state.output_img,
                realtime_update=True,
                box_color="blue",
                aspect_ratio=None
            )
            st.subheader("Cropped Image")
            st.image(cropped_image, caption="Cropped PCB Image", use_container_width=True)

            st.subheader("Run YOLOv8 Detection on Cropped Image")
            cropped_np = np.array(cropped_image)
            cropped_bgr = cv2.cvtColor(cropped_np, cv2.COLOR_RGB2BGR)

            # Dynamic Scaling Based on Captured Image Dimensions
            image_height, image_width = cropped_bgr.shape[:2]
            scaling_factor = min(image_width / 640, image_height / 480)  # Baseline scaling reference

            # YOLO Prediction with Scaled Detection Results
            results = model.predict(source=cropped_bgr, save=False, conf=0.25)
            if len(results[0].boxes) > 0:
                # Adjust annotation size
                annotated_cropped = results[0].plot(
                    font_size=int(12 * scaling_factor)  # Scale label font size
                )
                st.image(annotated_cropped, caption="Detected Defects on Cropped Image", use_container_width=True)
                st.write(f"Detected Defects: {len(results[0].boxes)}")
            else:
                st.info("No defects detected in the cropped image.")

    # Next Button to go to the Template Image Upload page
    next_button = st.button("Continue to home page")
    if next_button:
        st.session_state.page = "home"  # Go to Capture Output Image PAge
        st.rerun()  # Use st.rerun() instead of deprecated experimental_rerun



# Initialize session state if it's the first time
if "page" not in st.session_state:
    st.session_state.page = "home"

# Conditional page rendering based on the current page in session state
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "capture_output_image":
    capture_output_image_page()



