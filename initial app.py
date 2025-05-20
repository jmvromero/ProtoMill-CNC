import customtkinter as ctk
from PIL import Image, ImageTk
import subprocess

# Configure appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class ProtoMillApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.idle_timeout = 5  # Seconds of inactivity before showing slideshow
        self.idle_timer = None
        self.slideshow_index = 0
        self.slideshow_messages = [
            "ProtoMill CNC Control System",
            "Precision Milling Solutions",
            "Automated Defect Detection",
            "Easy-to-Use Interface",
            "Safety First: Always Wear Protective Gear"
        ]

        # Modern color scheme
        self.primary_color = "#2563EB"  # Blue-600
        self.secondary_color = "#1E40AF"  # Blue-800
        self.accent_color = "#DB2777"  # Pink-600
        self.dark_bg = "#222222"  # Dark background for slideshow

        # Configure main window
        self.title("ProtoMill CNC")
        self.attributes('-fullscreen', True)
        self.configure(fg_color="white")  # Static white background

        # Create main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Create slideshow container
        self.slideshow_frame = ctk.CTkFrame(self, fg_color=self.dark_bg, corner_radius=0)
        self.slideshow_label = ctk.CTkLabel(self.slideshow_frame, text="",
                                            font=("Montserrat Bold", 48),
                                            text_color="white")
        self.slideshow_label.pack(expand=True, fill="both")
        self.slideshow_frame.pack_forget()

        # Load images
        try:
            self.cnc_img = ctk.CTkImage(light_image=Image.open("cnc-machine.png"),
                                        size=(120, 120))
            self.dd_img = ctk.CTkImage(light_image=Image.open("loupe.png"),
                                       size=(120, 120))
        except:
            self.cnc_img = None
            self.dd_img = None

        # Create UI elements
        self.create_widgets()

        # Bind activity events
        self.bind_activity_events()
        self.reset_idle_timer()

    def create_widgets(self):
        # Title label with modern styling
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=(20, 40))

        title_label = ctk.CTkLabel(title_frame, text="ProtoMill CNC",
                                   font=("Montserrat Bold", 48, "bold"),
                                   text_color=self.secondary_color)
        title_label.pack(side="left")

        # Decorative element
        decor = ctk.CTkLabel(title_frame, text="⚙",
                             font=("Arial", 32),
                             text_color=self.accent_color)
        decor.pack(side="left", padx=10)

        # Button container
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(expand=True, fill="both")

        # Grid configuration
        button_frame.columnconfigure(0, weight=1, uniform="buttons")
        button_frame.columnconfigure(1, weight=1, uniform="buttons")
        button_frame.rowconfigure(0, weight=1)

        # bCNC Button
        self.bCNC_button = ctk.CTkButton(
            button_frame,
            text="bCNC",
            font=("Montserrat SemiBold", 28),
            image=self.cnc_img,
            compound="top",
            width=300,
            height=200,
            corner_radius=24,
            border_width=0,
            fg_color="white",
            text_color=self.secondary_color,
            hover_color="#F3F4F6",
            command=self.launch_bCNC
        )
        self.bCNC_button.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Defect Detection Button
        self.dd_button = ctk.CTkButton(
            button_frame,
            text="Defect\nDetection",
            font=("Montserrat SemiBold", 28),
            image=self.dd_img,
            compound="top",
            width=300,
            height=200,
            corner_radius=24,
            border_width=0,
            fg_color="white",
            text_color=self.secondary_color,
            hover_color="#F3F4F6",
            command=self.launch_defect_detection
        )
        self.dd_button.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Footer
        footer = ctk.CTkLabel(self.main_frame,
                              text="© 2025 ProtoMill CNC | v2.0.0",
                              font=("Montserrat", 14),
                              text_color="#6B7280")
        footer.pack(side="bottom", pady=20)

    def bind_activity_events(self):
        for event in ['<Motion>', '<KeyPress>', '<ButtonPress>']:
            self.bind(event, self.on_activity)
            self.main_frame.bind(event, self.on_activity)

    def on_activity(self, event=None):
        self.reset_idle_timer()
        if self.slideshow_frame.winfo_ismapped():
            self.show_main_interface()

    def reset_idle_timer(self):
        if self.idle_timer:
            self.after_cancel(self.idle_timer)
        self.idle_timer = self.after(self.idle_timeout * 1000, self.show_slideshow)

    def show_main_interface(self):
        self.slideshow_frame.pack_forget()
        self.main_frame.pack(expand=True, fill="both", padx=50, pady=50)

    def show_slideshow(self):
        self.main_frame.pack_forget()
        self.slideshow_frame.pack(expand=True, fill="both")
        self.update_slideshow_content()
        self.slideshow_timer = self.after(3000, self.update_slideshow_content)

    def update_slideshow_content(self):
        self.slideshow_label.configure(text=self.slideshow_messages[self.slideshow_index])
        self.slideshow_index = (self.slideshow_index + 1) % len(self.slideshow_messages)
        self.slideshow_timer = self.after(3000, self.update_slideshow_content)

    def launch_bCNC(self):
        # Start serial bridge in background
        subprocess.Popen(["python3", "serial_bridge.py"])
        # Launch bCNC as before
        subprocess.Popen(["bCNC"])
        self.reset_idle_timer()

    def launch_defect_detection(self):
        subprocess.Popen(["streamlit", "run", "yolo-app.py"])
        self.reset_idle_timer()


if __name__ == "__main__":
    app = ProtoMillApp()
    app.mainloop()