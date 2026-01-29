import streamlit as st
import cv2
from PIL import Image
import numpy as np
from streamlit_cropper import st_cropper
from ultralytics import YOLO
import os
import pandas as pd
import seaborn as sns
import plotly.express as px
from datetime import datetime
import matplotlib.pyplot as plt

CLASS_NAMES = {
    0: "short",
    1: "spur",
    2: "spurious copper",
    3: "open",
    4: "mouse bite",
    5: "hole breakout",
    6: "conductor scratch",
    7: "conductor foreign object",
    8: "base material foreign object"
}

# Add after your existing session state initialization
if "defect_data" not in st.session_state:
    st.session_state.defect_data = pd.DataFrame(columns=[
        "timestamp", "defect_type", "confidence",
        "location_x", "location_y", "image_path"
    ])

if "uncertain_samples" not in st.session_state:
    st.session_state.uncertain_samples = []

# Get current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path construction for GitHub compatibility
model_path = os.path.join(script_dir, "train_results", "weights", "best.pt")
model = YOLO(model_path)

## Put this right after your imports
# Data directory setup
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, "defect_data.csv")

def load_defect_data():
    try:
        if os.path.exists(CSV_PATH):
            return pd.read_csv(CSV_PATH)
        return pd.DataFrame(columns=[
            "timestamp", "defect_type", "confidence",
            "location_x", "location_y", "image_path"
        ])
    except Exception as e:
        st.error(f"Error loading defect data: {str(e)}")
        return pd.DataFrame(columns=[
            "timestamp", "defect_type", "confidence",
            "location_x", "location_y", "image_path"
        ])

if "defect_data" not in st.session_state:
    st.session_state.defect_data = load_defect_data()


def save_defect_data():
    try:
        # Ensure directory exists
        os.makedirs(DATA_DIR, exist_ok=True)

        # Save to CSV
        st.session_state.defect_data.to_csv(CSV_PATH, index=False)

    except PermissionError:
        st.error("⚠️ Permission denied: Cannot save data file. Please check write permissions.")
    except Exception as e:
        st.error(f"⚠️ Error saving defect data: {str(e)}")


# Home Page (Overview & Introduction)
def home_page():
    # Set the title and introductory text
    st.title("InspectMill")
    st.write("""
    Welcome to the InspectMill, a PCB Defect Detection Tool powered by OpenCV and Streamlit. 
    This tool helps you to detect defects in your PCB designs by comparing a template PCB image 
    with an output image from your CNC machine.
    """)

    st.write("""
    ### Instructions:
    1. **Capture the Output Image**: Capture the PCB output image from your CNC machine.
    2. **Detection from Yolo-V8**: The app will use the model to detect the defects.
    3. **Results**: View the detected defects and download the results.
    """)

    # Next Button to go to the Template Image Upload page
    next_button = st.button("Next")
    if next_button:
        st.session_state.page = "capture_output_image"
        st.rerun()

    # Add navigation buttons after your existing content
    st.markdown("---")
    st.subheader("Advanced Features")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 View Analytics Dashboard"):
            st.session_state.page = "analytics"
            st.rerun()

    with col2:
        if st.button("🔍 Review Uncertain Detections"):
            st.session_state.page = "review_uncertain"
            st.rerun()


def capture_output_image_page():
    st.title("Capture or Detect PCB Defects")

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

    # Initialize session state
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False
    if 'captured_frame' not in st.session_state:
        st.session_state.captured_frame = None
    if 'output_img' not in st.session_state:
        st.session_state.output_img = None

    st.subheader("Capture PCB Output Image")

    # Camera control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Camera"):
            st.session_state.camera_active = True
    with col2:
        if st.button("Stop Camera"):
            st.session_state.camera_active = False
            st.session_state.captured_frame = None

    # Camera capture section
    if st.session_state.camera_active:
        cap = cv2.VideoCapture(0)
        FRAME_WINDOW = st.image([])

        # Capture and clear buttons
        capture_col, clear_col = st.columns(2)
        with capture_col:
            if st.button("Take Photo"):
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.session_state.captured_frame = Image.fromarray(frame_rgb)
                    st.session_state.output_img = st.session_state.captured_frame
                    st.session_state.camera_active = False
                    st.success("Photo captured!")
                cap.release()

        with clear_col:
            if st.button("Clear Photo"):
                st.session_state.captured_frame = None
                st.session_state.output_img = None
                st.session_state.camera_active = False

        # Show live feed
        while st.session_state.camera_active and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture frame")
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame)

        if 'cap' in locals():
            cap.release()

    # File uploader as alternative
    st.subheader("Or Upload an Image")
    uploaded_image = st.file_uploader("Upload PCB image (PNG, JPG, JPEG):",
                                      type=["png", "jpg", "jpeg"])

    # Process whichever image is available (camera or upload)
    current_image = None
    if st.session_state.captured_frame is not None:
        current_image = st.session_state.captured_frame
        st.subheader("Captured PCB Image")
    elif uploaded_image is not None:
        current_image = Image.open(uploaded_image)
        st.subheader("Uploaded PCB Image")

    if current_image is not None:
        st.image(current_image, caption="Selected Image", use_container_width=True)
        st.session_state.output_img = current_image

        # Rest of your existing processing code...
        # [Keep all your cropping and YOLO detection code exactly as is]

        # Cropping functionality
        st.subheader("Crop the Image")
        cropped_image = st_cropper(
            current_image,
            realtime_update=True,
            box_color="blue",
            aspect_ratio=None
        )

        st.subheader("Cropped Image")
        st.image(cropped_image, caption="Cropped PCB Image", use_container_width=True)

        st.subheader("Run YOLOv8 Detection on Cropped Image")
        cropped_np = np.array(cropped_image)
        cropped_bgr = cv2.cvtColor(cropped_np, cv2.COLOR_RGB2BGR)

        st.subheader("Preprocessed Image")
        st.image(cropped_bgr, caption="Preprocessed PCB Image", use_container_width=True)

        # Dynamic Scaling Based on Captured Image Dimensions
        image_height, image_width = cropped_bgr.shape[:2]
        scaling_factor = min(image_width / 640, image_height / 640)

        # YOLO Prediction with Scaled Detection Results
        results = model.predict(source=cropped_bgr, save=False, conf=0.25)

        if len(results[0].boxes) > 0:
            annotated_cropped = results[0].plot(font_size=int(12 * scaling_factor))

            # Initialize counters
            defect_counts = {name: 0 for name in CLASS_NAMES.values()}
            type_details = []

            # Data collection
            for box in results[0].boxes:
                class_id = int(box.cls)
                defect_type = CLASS_NAMES.get(class_id, "unknown")
                confidence = float(box.conf)

                # Update counts
                defect_counts[defect_type] += 1

                # Store details for logging
                type_details.append(f"{defect_type} ({confidence:.2f})")

                # In your detection loop where you add new defects:
                new_row = {
                    "timestamp": datetime.now().isoformat(),
                    "defect_type": model.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "location_x": int((box.xywh[0][0] + box.xywh[0][2] / 2).item()),
                    "location_y": int((box.xywh[0][1] + box.xywh[0][3] / 2).item()),
                    "image_path": f"defects/{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                }
                st.session_state.defect_data = pd.concat(
                    [st.session_state.defect_data, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                save_defect_data()  # Add this right after adding new data

                # Flag low-confidence samples for review
                if float(box.conf) < 0.4:
                    # Create annotated image for review
                    annotated_img = results[0].plot()
                    st.session_state.uncertain_samples.append({
                        "image": annotated_img,  # Store the annotated image
                        "prediction": new_row
                    })

            st.image(annotated_cropped, caption="Detected Defects on Cropped Image",
                     use_container_width=True)
            # Show summary with types
            st.write(f"**Total Detected Defects:** {len(results[0].boxes)}")
            st.write("**Defect Breakdown:**")

            # Create two columns for better layout
            col1, col2 = st.columns(2)

            with col1:
                # Detailed list
                st.write("Detected defects:")
                for detail in type_details:
                    st.write(f"- {detail}")

            with col2:
                # Count summary
                st.write("Defect counts:")
                for defect, count in defect_counts.items():
                    if count > 0:
                        st.write(f"- {defect}: {count}")

        else:
            st.info("No defects detected in the cropped image.")

    # Next Button to go to the Template Image Upload page
    next_button = st.button("Continue to home page")
    if next_button:
        st.session_state.page = "home"
        st.rerun()

def analytics_page():
    st.title("Defect Analytics Dashboard")

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    # Single download button for CSV
    try:
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=f,
                    file_name="defect_data.csv",
                    mime="text/csv",
                    help="Download all defect data as CSV file"
                )
        else:
            st.warning("No data available yet - detect some defects first")
    except Exception as e:
        st.error(f"⚠️ Error preparing download: {str(e)}")


    # Rest of your existing analytics code...
    if st.session_state.defect_data.empty:
        st.warning("No defect data collected yet!")
        return

    DEFECT_MAP = {
        0: "short",
        1: "spur",
        2: "spurious copper",
        3: "open",
        4: "mouse bite",
        5: "hole breakout",
        6: "conductor scratch",
        7: "conductor foreign object",
        8: "base material foreign object"
    }

    # Create a modified copy for visualization
    df = st.session_state.defect_data.copy()

    # Convert numerical types to human-readable names
    df['defect_type'] = df['defect_type'].apply(
        lambda x: DEFECT_MAP[int(x)] if str(x).isdigit() else x
    )

    # Your existing visualization code remains the same...
    # Modified visualization code
    st.subheader("Defect Distribution")
    defect_counts = df["defect_type"].value_counts()
    fig = px.bar(defect_counts,
                 x=defect_counts.index,
                 y=defect_counts.values,
                 labels={'x': 'Defect Type', 'y': 'Count'})
    st.plotly_chart(fig)

    # Temporal Trends
    st.subheader("Defect Trends Over Time")
    temporal_data = df.groupby(
        [pd.to_datetime(df["timestamp"]).dt.date, "defect_type"]
    ).size().unstack()
    st.line_chart(temporal_data)

    # Heatmap Visualization
    st.subheader("Defect Location Heatmap")
    plt.figure(figsize=(10, 6))
    sns.kdeplot(
        x=st.session_state.defect_data["location_x"],
        y=st.session_state.defect_data["location_y"],
        cmap="Reds", fill=True
    )
    st.pyplot(plt.gcf())


def review_uncertain_page():
    st.title("Review Uncertain Detections")

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    if not st.session_state.uncertain_samples:
        st.info("No uncertain detections to review!")
        return

    st.write(f"Found {len(st.session_state.uncertain_samples)} uncertain detections (confidence < 0.4)")

    for i, sample in enumerate(st.session_state.uncertain_samples[:10]):  # Show first 10 samples
        st.markdown("---")
        st.subheader(f"Sample {i + 1}")

        # Convert BGR to RGB for display (since we stored the annotated image)
        img_rgb = cv2.cvtColor(sample["image"], cv2.COLOR_BGR2RGB)
        st.image(img_rgb, caption="Detected defect with bounding box", use_container_width=True)

        st.write(f"""
        - **Predicted defect**: {sample["prediction"]["defect_type"]}
        - **Confidence**: {sample["prediction"]["confidence"]:.2f}
        - **Location**: ({sample["prediction"]["location_x"]}, {sample["prediction"]["location_y"]})
        - **Timestamp**: {sample["prediction"]["timestamp"]}
        """)


# Initialize session state if it's the first time
if "page" not in st.session_state:
    st.session_state.page = "home"

# Conditional page rendering based on the current page in session state
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "capture_output_image":
    capture_output_image_page()
elif st.session_state.page == "analytics":
    analytics_page()
elif st.session_state.page == "review_uncertain":
    review_uncertain_page()