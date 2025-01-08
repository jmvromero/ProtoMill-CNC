import streamlit as st
import cv2
from PIL import Image
import numpy as np

# Home Page (Overview & Introduction)
def home_page():
    # Set the title and introductory text
    st.title("InspectMill")
    st.write("""
    Welcome to the InspectMill, a PCB Defect Detection Tool powered by OpenCV and Streamlit. This tool helps you to detect defects in your PCB designs by comparing a template PCB image with an output image from your CNC machine.
    """)

    st.write("""
    ### Instructions:
    1. **Upload the Template Image**: You will upload a clean, reference image of your PCB design.
    2. **Capture the Output Image**: After processing the template image, you will upload the PCB output image from your CNC machine.
    3. **Align the Images**: The app will align the two images for accurate comparison.
    4. **Defect Detection**: The system will detect and highlight any defects by comparing the images.
    5. **Results**: View the detected defects and download the results.
    """)

    # Next Button to go to the Template Image Upload page
    next_button = st.button("Next")
    if next_button:
        st.session_state.page = "template_upload"  # Go to Template Image Upload Page
        st.rerun()  # Use st.rerun() instead of deprecated experimental_rerun

# Template Image Upload Page
def template_image_upload_page():
    st.title("Upload Template PCB Image")

    # Show a Back button to return to the Home Page
    back_button = st.button("Back")
    if back_button:
        st.session_state.page = "home"  # Navigate to Home Page
        st.rerun()  # Use st.rerun() instead of deprecated experimental_rerun

    # Upload template PCB image
    uploaded_template_img = st.file_uploader("Choose a template PCB image...", type=["jpg", "png", "jpeg"])

    if uploaded_template_img is not None:
        # Open the uploaded image
        template_image = Image.open(uploaded_template_img)
        st.image(template_image, caption="Uploaded Template Image.", use_container_width=True)

        # Convert the uploaded image to an OpenCV format (numpy array)
        img_array = np.array(template_image)

        # Step 1: Convert to Grayscale
        gray_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        st.image(gray_image, caption="Grayscale Template Image", use_container_width=True)

        # Step 2: Resize the image
        resized_image = cv2.resize(gray_image, (750, 450))
        st.image(resized_image, caption="Resized Template Image", use_container_width=True)

        # Step 3: Apply Gaussian Blur
        blurred_image = cv2.GaussianBlur(resized_image, (3, 3), 0)
        st.image(blurred_image, caption="Blurred Template Image (Gaussian)", use_container_width=True)

        # Step 4: Apply Thresholding
        _, thresholded_image = cv2.threshold(blurred_image, 128, 255, cv2.THRESH_BINARY)
        st.image(thresholded_image, caption="Thresholded Template Image", use_container_width=True)

        # Button to continue to the next page
        next_button = st.button("Next")
        if next_button:
            # Save the processed image in session state for further use
            st.session_state.template_img = uploaded_template_img
            # Navigate to the Capture Output Image page
            st.session_state.page = "capture_output_image"
            st.rerun()  # Use st.rerun() instead of deprecated experimental_rerun


# Capture Output Image Page
def capture_output_image_page():
    st.title("Capture Output PCB Image from Camera")

    # Show a Back button to return to the Template Image Upload Page
    back_button = st.button("Back")
    if back_button:
        st.session_state.page = "template_upload"  # Navigate to Template Image Upload Page
        st.rerun()  # Refresh the page

    # Capture Image Using Camera
    camera_image = st.camera_input("Capture Output Image from Camera")

    if camera_image is not None:
        # Convert the image to an OpenCV format
        image = Image.open(camera_image)
        img_array = np.array(image)

        # Show the captured image
        st.image(img_array, caption="Captured Output PCB Image.", use_column_width=True)

        # Save the captured image in session state for further processing
        st.session_state.output_img = camera_image

        # Show Retake and Proceed buttons
        retake_button = st.button("Retake Image")
        if retake_button:
            st.session_state.output_img = None  # Reset the image for retake
            st.rerun()  # Trigger the rerun to clear the current image

        proceed_button = st.button("Proceed with Image")
        if proceed_button:
            # Confirm that the image is ready for processing
            st.session_state.page = "image_alignment"  # Navigate to Image Alignment Page
            st.rerun()  # Use st.rerun() to refresh and go to next page


# Initialize session state if it's the first time
if "page" not in st.session_state:
    st.session_state.page = "home"

# Conditional page rendering based on the current page in session state
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "template_upload":
    template_image_upload_page()
elif st.session_state.page == "capture_output_image":
    capture_output_image_page()

