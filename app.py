import streamlit as st
import cv2
from PIL import Image
import numpy as np
from streamlit_cropper import st_cropper
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

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
        st.experimental_rerun()  # Use st.rerun() instead of deprecated experimental_rerun

# Template Image Upload Page
def template_image_upload_page():
    st.title("Upload Template PCB Image")

    # Show a Back button to return to the Home Page
    back_button = st.button("Back")
    if back_button:
        st.session_state.page = "home"  # Navigate to Home Page
        st.experimental_rerun()  # Use st.rerun() instead of deprecated experimental_rerun

    # Upload template PCB image
    uploaded_template_img = st.file_uploader("Choose a template PCB image...", type=["jpg", "png", "jpeg"])

    if uploaded_template_img is not None:
        # Open the uploaded image
        template_image = Image.open(uploaded_template_img)
        st.image(template_image, caption="Uploaded Template Image.", use_column_width=True)

        # Convert the uploaded image to an OpenCV format (numpy array)
        img_array = np.array(template_image)

        # Step 1: Convert to Grayscale
        gray_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        st.image(gray_image, caption="Grayscale Template Image", use_column_width=True)

        # Step 2: Resize the image
        resized_image = cv2.resize(gray_image, (750, 450))
        st.image(resized_image, caption="Resized Template Image", use_column_width=True)

        # Step 3: Apply Gaussian Blur
        blurred_image = cv2.GaussianBlur(resized_image, (3, 3), 0)
        st.image(blurred_image, caption="Blurred Template Image (Gaussian)", use_column_width=True)

        # Step 4: Apply Thresholding
        _, thresholded_image = cv2.threshold(blurred_image, 128, 255, cv2.THRESH_BINARY)
        st.image(thresholded_image, caption="Thresholded Template Image", use_column_width=True)

        # Button to continue to the next page
        next_button = st.button("Next")
        if next_button:
            # Save the processed image in session state for further use
            st.session_state.template_img = uploaded_template_img
            # Navigate to the Capture Output Image page
            st.session_state.page = "capture_output_image"
            st.experimental_rerun()  # Use st.rerun() instead of deprecated experimental_rerun


def capture_output_image_page():
    st.title("Capture or Upload Output PCB Image")

    # Back button to return to the Template Image Upload Page
    if st.button("Back"):
        st.session_state.page = "template_upload"
        st.experimental_rerun()

    # Camera input to capture the output PCB image
    st.subheader("Capture Output Image from Camera")
    camera_image = st.camera_input("Capture Output Image from Camera")

    # File uploader to upload the output PCB image
    st.subheader("Or Upload Output Image")
    uploaded_image = st.file_uploader("Upload your output image (e.g., PNG, JPG, JPEG):",
                                      type=["png", "jpg", "jpeg"])

    # Check if camera image or uploaded image is available
    if camera_image or uploaded_image:
        st.subheader("Selected Output PCB Image")

        # Determine the source of the image
        if camera_image is not None:
            # Use the camera-captured image
            image = Image.open(camera_image)
            st.write("Image captured using the camera.")
        else:
            # Use the uploaded image
            image = Image.open(uploaded_image)
            st.write("Image uploaded successfully.")

        # Display the selected image
        st.image(image, caption="Selected Output Image", use_column_width=True)

        # Store the selected image in session state
        st.session_state.output_img = image

        # Cropping tool similar to Google Lens
        st.subheader("Crop the Image (Google Lens-like experience)")

        # Allow the user to crop the image with interactive cropping
        cropped_image = st_cropper(
            st.session_state.output_img,
            realtime_update=True,  # Reflect cropping changes in real-time
            box_color="blue",  # Highlight cropping box with blue
            aspect_ratio=None  # Free aspect-ratio cropping
        )
        st.subheader("Cropped Image")
        st.image(cropped_image, caption="Cropped Output PCB Image", use_column_width=True)

        # Store the cropped image in session state
        st.session_state.cropped_img = cropped_image

        # User Actions
        st.subheader("Actions")
        if st.button("Save and Proceed"):
            if "cropped_img" in st.session_state:
                st.session_state.page = "image_alignment"
                st.experimental_rerun()
    else:
        st.warning("Please either capture an image using your camera or upload one.")


def image_alignment():
    st.title("Image Alignment")
    st.write("This includes the process of ORB, Feature Matching, and Homography Transformation.")

    if st.button("Back"):
        st.session_state.page = "capture_output_image"
        st.experimental_rerun()

    # Access the uploaded template image from session state
    if "template_img" and "cropped_img" in st.session_state:
        #Displaying the captured image
        cropped_opencv_image = np.array(st.session_state.cropped_img)
        gray_image1 = cv2.cvtColor(cropped_opencv_image, cv2.COLOR_RGB2GRAY)
        resized_image1 = cv2.resize(gray_image1, (750, 450))
        img1 = cv2.GaussianBlur(resized_image1, (3, 3), 0)
        st.image(img1, caption="Grayscale Image", use_column_width=True)

        #Displaying the template image
        uploaded_file = st.session_state.template_img  # Retrieve the uploaded file
        template_image = Image.open(uploaded_file)  # Open it as a PIL image
        uploaded_template_img = np.array(template_image)  # Convert it to a NumPy array
        gray_image2 = cv2.cvtColor(uploaded_template_img, cv2.COLOR_RGB2GRAY)  # Convert to grayscale
        resized_image2 = cv2.resize(gray_image2, (750, 450))
        blurred_image2 = cv2.GaussianBlur(resized_image2, (3, 3), 0)
        _, img2 = cv2.threshold(blurred_image2, 128, 255, cv2.THRESH_BINARY)
        st.image(img2, caption="Grayscale Image from Template Upload Page", use_column_width=True)

        #ORB Detection
        st.subheader("ORB Detection")
        orb = cv2.ORB_create()

        #Template Image
        kp1, des1 = orb.detectAndCompute(img2, None)
        img_template = cv2.drawKeypoints(img2, kp1, None, color=(0, 255, 0), flags=0)
        st.image(img_template, caption="ORB Detection", use_column_width=True)

        #Captured Image
        kp2, des2 = orb.detectAndCompute(img1, None)
        img_captured = cv2.drawKeypoints(img1, kp2, None, color=(0, 255, 0), flags=0)
        st.image(img_captured, caption="ORB Detection", use_column_width=True)

        #Feature Matching
        st.subheader("Feature Matching")
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        img3 = cv2.drawMatches(img2, kp1, img1, kp2, matches[:10], None, flags=2)
        st.image(img3, caption="Feature Matching", use_column_width=True)

        #Homography Calculation
        st.subheader("Homography Calculation")
        dmatches = sorted(matches, key=lambda x: x.distance)

        src_pts = np.float32([kp1[m.queryIdx].pt for m in dmatches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in dmatches]).reshape(-1, 1, 2)

        h, status = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        st.write('calculated homography is', h)

        # Warping: Transforming the captured image using the homography matrix
        if h is not None:
            st.subheader("Warping")
            # Warp the perspective of the captured image to match the template
            img4 = cv2.warpPerspective(img1, h, (img2.shape[1], img2.shape[0]))

            # Convert warped image to RGB for proper displaying in Streamlit (optional)
            img4_rgb = cv2.cvtColor(img4, cv2.COLOR_GRAY2RGB)

            # Display warped image in Streamlit
            st.image(img4_rgb, caption="Warped Image using Homography", use_column_width=True)

            # Optionally, overlay or compare with the template
            overlay = cv2.addWeighted(img2, 0.5, img4, 0.5, 0)  # Alpha blend for visualization
            st.image(overlay, caption="Overlay of Warped Image and Template", use_column_width=True)
            st.session_state.warped_image = img4  # Save the warped align image
            st.session_state.template_image = img2  # Save the processed template image
        else:
            st.error("Homography failed. Unable to compute the warped image.")

        # Save the images to session state for use in other functions/pages



    else:
        st.warning("Template image not found in session state. Please upload it on the Template Image Upload page.")

    # User Actions
    st.subheader("Actions")
    if st.button("Next"):
        # Set the session state to the next page (e.g., "image_subtraction_and_results")
        st.session_state.page = "image_subtraction_and_results"
        st.experimental_rerun()


def image_subtraction_and_results():
    st.title("Image Subtraction and Contour Detection")

    # Back button to return to the previous page
    if st.button("Back"):
        st.session_state.page = "image_alignment"
        st.experimental_rerun()

    # Ensure that both template image (`img2`) and aligned image (`img4`) exist.
    if "template_image" in st.session_state and "warped_image" in st.session_state:
        img2 = st.session_state.template_image  # Retrieve template image
        img4 = st.session_state.warped_image  # Retrieve warped image

        # Perform image subtraction
        sub_img = cv2.subtract(img2, img4)

        # Display the subtracted result
        st.subheader("Resultant Image After Subtraction")
        plt.figure(figsize=(10, 6))
        plt.imshow(sub_img, cmap="gray")
        st.pyplot(plt)

        # Median blur to reduce noise
        final_img = cv2.medianBlur(sub_img, 5)

        # Display the final binary image
        st.subheader("Final Binary Image for Defect Detection (Noise Reduced)")
        plt.figure(figsize=(10, 6))
        plt.imshow(final_img, cmap="gray")
        st.pyplot(plt)

        # Contour detection
        st.subheader("Contour Detection")
        cnts = cv2.findContours(
            final_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )[-2]
        blobs = [cnt for cnt in cnts if 0 < cv2.contourArea(cnt) < 300]

        # Display the number of defects
        num_defects = len(blobs)
        st.write(f"**Number of defects detected:** {num_defects}")

        # Save results to a persistent CSV file
        csv_file = "defects_data.csv"
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if os.path.exists(csv_file):  # Load existing data
            defects_data = pd.read_csv(csv_file)
        else:  # Create a new DataFrame if file doesn't exist
            defects_data = pd.DataFrame(columns=["Date", "Defects Detected"])

        # Create a new DataFrame with the current result
        new_data = pd.DataFrame([{"Date": current_date, "Defects Detected": num_defects}])

        # Concatenate the new data to the existing DataFrame
        defects_data = pd.concat([defects_data, new_data], ignore_index=True)

        # Graph 1: Number of PCBs inspected vs Defects
        st.subheader("Number of PCBs Inspected vs Defects")
        plt.figure(figsize=(8, 5))
        plt.bar(defects_data.index + 1, defects_data["Defects Detected"], color="blue")
        plt.xlabel("PCB Count")
        plt.ylabel("Defects Detected")
        plt.title("Defects Detected per PCB")
        st.pyplot(plt)

        # Graph 2: Number of Defects Detected vs Date
        st.subheader("Number of Defects Detected Over Time")
        plt.figure(figsize=(10, 5))
        plt.plot(
            pd.to_datetime(defects_data["Date"]),
            defects_data["Defects Detected"],
            marker="o",
            linestyle="-",
            color="red",
        )
        plt.xlabel("Date")
        plt.ylabel("Defects Detected")
        plt.title("Defects Detected Over Time")
        plt.xticks(rotation=45)
        st.pyplot(plt)

    else:
        st.error(
            "Images are not properly loaded. Please make sure template and captured images are correctly processed.")
    # Add a 'Continue' button to go back to the home page
    if st.button("Continue"):
        st.session_state.page = "home"
        st.experimental_rerun()



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
elif st.session_state.page == "image_alignment":
    image_alignment()
elif st.session_state.page == "image_subtraction_and_results":
    image_subtraction_and_results()


