import customtkinter as ctk
from PIL import Image, ImageTk

# Appearance mode (It could be Dark or Light based on the system)
ctk.set_appearance_mode("Light")

# Default theme (I choose blue for the mean time)
ctk.set_default_color_theme("blue")

# This will be the application window
app = ctk.CTk()
app.title("ProtoMill CNC")
app.geometry("480x320")
app.resizable(True, True)  # Allow window resizing

# Create a fixed-size frame to hold the content
content_frame = ctk.CTkFrame(app, width=480, height=320, fg_color="transparent")
content_frame.place(relx=0.5, rely=0.5, anchor="center")

# Label
label = ctk.CTkLabel(content_frame, text="ProtoMill CNC", font=("Montserrat Bold", 25), text_color="black")
label.place(relx=0.5, rely=0.3, anchor="center")

# Icons for buttons
cncImg = Image.open("cnc-machine.png")
ddImg = Image.open("loupe.png")

# bCNCButton
bCNCButton = ctk.CTkButton(content_frame, text="bCNC", font=("Montserrat", 15), text_color="black",
                           corner_radius=10, fg_color="white",
                           border_color="#060270", hover_color="#CECECE",
                           border_width=2, image=ctk.CTkImage(dark_image=cncImg, light_image=cncImg))
bCNCButton.place(relx=0.5, rely=0.5, anchor="center")

# inspectMillButton
inspectMillButton = ctk.CTkButton(content_frame, text="Defect Detection", font=("Montserrat", 15), text_color="black",
                                   corner_radius=10, fg_color="white",
                                   border_color="#060270", hover_color="#CECECE",
                                   border_width=2, image=ctk.CTkImage(dark_image=ddImg, light_image=ddImg))
inspectMillButton.place(relx=0.5, rely=0.7, anchor="center")

# Run the application
app.mainloop()
