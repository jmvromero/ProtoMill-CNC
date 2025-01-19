import customtkinter as ctk
from PIL import Image, ImageTk
import subprocess  # Import subprocess to run the Streamlit app


# Appearance mode (It could be Dark or Light based on the system)
ctk.set_appearance_mode("Light")

# Default theme (I choose blue for the mean time)
ctk.set_default_color_theme("blue")

# This will be the application window
app = ctk.CTk(fg_color="white")
app.iconbitmap("cnc-machine.ico")
app.title("ProtoMill CNC")
app.geometry("480x320")  # Start with a smaller window size (480x320)
app.resizable(False, False)  # Allow window resizing

# Load the background image (1920x1080)
bg_image_path = "background.png"  # Replace with your actual image path
bg_image = Image.open(bg_image_path)
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a fixed-size frame to hold the content
content_frame = ctk.CTkFrame(app, width=480, height=320, fg_color="transparent")
content_frame.place(relx=0.5, rely=0.5, anchor="center")

# Label inside the content frame
label = ctk.CTkLabel(content_frame, text="ProtoMill CNC", font=("Montserrat Bold", 25), text_color="black")
label.place(relx=0.5, rely=0.3, anchor="center")

# Load icons for buttons
cncImg = Image.open("cnc-machine.png")
ddImg = Image.open("loupe.png")

# Function to launch bCNC
def launch_bCNC():
    try:
        # Use the absolute path to the Candle executable
        subprocess.Popen(["bCNC"])
    except FileNotFoundError:
        print("Candle application not found. Ensure the path is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



# Function to launch the defect detection app
def launch_defect_detection():
    subprocess.Popen(["streamlit", "run", "yolo-app.py"])


# Define bCNCButton with command tied to launch_candle
bCNCButton = ctk.CTkButton(content_frame, text="bCNC", font=("Montserrat", 15), text_color="black",
                           corner_radius=10, fg_color="white",
                           border_color="#060270", hover_color="#CECECE",
                           border_width=2, image=ctk.CTkImage(dark_image=cncImg, light_image=cncImg),
                           command=launch_bCNC)  # Pass the reference to the function, not a call
bCNCButton.place(relx=0.5, rely=0.5, anchor="center")

# Define Defect Detection Button (inspectMillButton)
inspectMillButton = ctk.CTkButton(content_frame, text="Defect Detection", font=("Montserrat", 15), text_color="black",
                                  corner_radius=10, fg_color="white",
                                  border_color="#060270", hover_color="#CECECE",
                                  border_width=2, image=ctk.CTkImage(dark_image=ddImg, light_image=ddImg),
                                  command=launch_defect_detection)  # Command to launch the defect detection app
inspectMillButton.place(relx=0.5, rely=0.7, anchor="center")


# Run the application
app.mainloop()