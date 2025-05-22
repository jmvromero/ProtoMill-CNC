import customtkinter as ctk
from PIL import Image, ImageTk
import subprocess
import requests
from tkinter import messagebox
import webbrowser

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
            "PCB Design Integration",
            "Easy-to-Use Interface",
            "Safety First: Always Wear Protective Gear"
        ]
        self.templates = [
            {"name": "2x2 Simple Design Mill", "url": "https://raw.githubusercontent.com/jmvromero/ProtoMill-CNC/master/Simple%20Design/%5BFinal%5D2x2Gerber_TopLayer.GTL_iso_combined_cnc.nc"},
            {"name": "2x2 Simple Design Drill", "url": "https://raw.githubusercontent.com/jmvromero/ProtoMill-CNC/master/Simple%20Design/%5BFinal%5D2x2Drill_PTH_Through.DRL_cnc.nc"},
            {"name": "4x4 Complex Design Mill", "url": "https://raw.githubusercontent.com/jmvromero/ProtoMill-CNC/master/Complex%20Design/%5B4x4%5DGerber_TopLayer.GTL_iso_combined_cnc.nc"},
            {"name": "4x4 Complex Design Drill", "url": "https://raw.githubusercontent.com/jmvromero/ProtoMill-CNC/master/Complex%20Design/%5B4x4%5DDrill_PTH_Through.DRL_cnc.nc"}
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

        # Create other frames
        self.create_pcb_interface()
        self.create_slideshow()
        self.create_templates_interface()
        self.create_new_interface()

        # Load images
        self.load_images()

        # Create UI elements
        self.create_widgets()

        # Bind activity events
        self.bind_activity_events()
        self.reset_idle_timer()

    def create_slideshow(self):
        self.slideshow_frame = ctk.CTkFrame(self, fg_color=self.dark_bg, corner_radius=0)
        self.slideshow_label = ctk.CTkLabel(self.slideshow_frame, text="",
                                            font=("Montserrat Bold", 48),
                                            text_color="white")
        self.slideshow_label.pack(expand=True, fill="both")

    def load_images(self):
        try:
            image_size = (120, 120)
            self.cnc_img = ctk.CTkImage(light_image=Image.open("cnc-machine.png"), size=image_size)
            self.dd_img = ctk.CTkImage(light_image=Image.open("loupe.png"), size=image_size)
            self.pcb_img = ctk.CTkImage(light_image=Image.open("pcb.png"), size=image_size)
        except Exception as e:
            print(f"Error loading images: {e}")
            self.cnc_img = self.dd_img = self.pcb_img = None

    def create_widgets(self):
        # Title label
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=(20, 40))

        ctk.CTkLabel(title_frame, text="ProtoMill CNC",
                     font=("Montserrat Bold", 48, "bold"),
                     text_color=self.secondary_color).pack(side="left")
        ctk.CTkLabel(title_frame, text="⚙", font=("Arial", 32),
                     text_color=self.accent_color).pack(side="left", padx=10)

        # Button container
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(expand=True, fill="both")

        # Configure grid
        for i in range(3):
            button_frame.columnconfigure(i, weight=1, uniform="buttons")

        # Buttons
        buttons = [
            ("PCB Design", self.pcb_img, self.show_pcb_interface),
            ("bCNC", self.cnc_img, self.launch_bCNC),
            ("Defect\nDetection", self.dd_img, self.launch_defect_detection)
        ]

        for col, (text, img, cmd) in enumerate(buttons):
            ctk.CTkButton(button_frame, text=text, font=("Montserrat SemiBold", 28),
                          image=img, compound="top", width=300, height=300,
                          corner_radius=24, fg_color="white", text_color=self.secondary_color,
                          hover_color="#F3F4F6", command=cmd
                          ).grid(row=0, column=col, padx=20, pady=20, sticky="nsew")

        # Footer
        ctk.CTkLabel(self.main_frame, text="© 2025 ProtoMill CNC | v2.0.0",
                     font=("Montserrat", 14), text_color="#6B7280").pack(side="bottom", pady=20)

    def create_pcb_interface(self):
        self.pcb_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Title
        ctk.CTkLabel(self.pcb_frame, text="PCB Design",
                     font=("Montserrat Bold", 48),
                     text_color=self.secondary_color).pack(pady=(20, 40))

        # Options
        options_frame = ctk.CTkFrame(self.pcb_frame, fg_color="transparent")
        options_frame.pack(expand=True, fill="both", padx=100, pady=50)

        ctk.CTkButton(options_frame, text="Templated Designs",
                      font=("Montserrat SemiBold", 28), height=100,
                      command=self.show_templates).pack(fill="x", pady=20)
        ctk.CTkButton(options_frame, text="Create New Design",
                      font=("Montserrat SemiBold", 28), height=100,
                      command=self.show_create_new).pack(fill="x", pady=20)

        # Back button
        ctk.CTkButton(self.pcb_frame, text="Back to Main Menu",
                      font=("Montserrat", 16), command=self.show_main_interface
                      ).pack(side="bottom", pady=20)

    def create_templates_interface(self):
        self.templates_frame = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(self.templates_frame, text="Choose a Template",
                     font=("Montserrat Bold", 48),
                     text_color=self.secondary_color).pack(pady=(20, 40))

        scroll_frame = ctk.CTkScrollableFrame(self.templates_frame)
        scroll_frame.pack(expand=True, fill="both", padx=50, pady=20)

        for template in self.templates:
            ctk.CTkButton(scroll_frame, text=template["name"],
                          font=("Montserrat", 20),
                          command=lambda t=template: self.download_template(t["url"])
                          ).pack(fill="x", pady=5)

        ctk.CTkButton(self.templates_frame, text="Back",
                      font=("Montserrat", 16),
                      command=lambda: self.switch_frame(self.pcb_frame)
                      ).pack(side="bottom", pady=20)

    def create_new_interface(self):
        self.create_new_frame = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(self.create_new_frame, text="Create New Design",
                     font=("Montserrat Bold", 48),
                     text_color=self.secondary_color).pack(pady=(20, 40))

        options_frame = ctk.CTkFrame(self.create_new_frame, fg_color="transparent")
        options_frame.pack(expand=True, fill="both", padx=100, pady=50)

        ctk.CTkButton(options_frame, text="Open KiCAD",
                      font=("Montserrat SemiBold", 28), height=100,
                      command=self.launch_kicad).pack(fill="x", pady=20)
        ctk.CTkButton(options_frame, text="Open EasyEDA",
                      font=("Montserrat SemiBold", 28), height=100,
                      command=self.launch_easyeda).pack(fill="x", pady=20)

        ctk.CTkButton(self.create_new_frame, text="Back",
                      font=("Montserrat", 16),
                      command=lambda: self.switch_frame(self.pcb_frame)
                      ).pack(side="bottom", pady=20)

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
        self.hide_all_frames()
        self.main_frame.pack(expand=True, fill="both", padx=50, pady=50)

    def show_pcb_interface(self):
        self.hide_all_frames()
        self.pcb_frame.pack(expand=True, fill="both", padx=50, pady=50)

    def show_templates(self):
        self.hide_all_frames()
        self.templates_frame.pack(expand=True, fill="both", padx=50, pady=50)

    def show_create_new(self):
        self.hide_all_frames()
        self.create_new_frame.pack(expand=True, fill="both", padx=50, pady=50)

    def show_slideshow(self):
        self.hide_all_frames()
        self.slideshow_frame.pack(expand=True, fill="both")
        self.update_slideshow_content()

    def hide_all_frames(self):
        for frame in [self.main_frame, self.pcb_frame,
                      self.templates_frame, self.create_new_frame,
                      self.slideshow_frame]:
            frame.pack_forget()

    def switch_frame(self, target_frame):
        self.hide_all_frames()
        target_frame.pack(expand=True, fill="both", padx=50, pady=50)

    def update_slideshow_content(self):
        self.slideshow_label.configure(text=self.slideshow_messages[self.slideshow_index])
        self.slideshow_index = (self.slideshow_index + 1) % len(self.slideshow_messages)
        self.slideshow_timer = self.after(3000, self.update_slideshow_content)

    def download_template(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            filename = url.split("/")[-1]
            with open(filename, 'wb') as f:
                f.write(response.content)
            subprocess.Popen(["bCNC", filename])
            messagebox.showinfo("Success", f"Downloaded {filename} successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")

    def launch_kicad(self):
        try:
            subprocess.Popen(["kicad"])
        except FileNotFoundError:
            messagebox.showerror("Error", "KiCAD not found. Please install KiCAD first.")

    def launch_easyeda(self):
        webbrowser.open("https://easyeda.com/editor")

    def launch_bCNC(self):
        subprocess.Popen(["python3", "serial_bridge.py"])
        subprocess.Popen(["bCNC"])
        self.reset_idle_timer()

    def launch_defect_detection(self):
        subprocess.Popen(["streamlit", "run", "yolo-app.py"])
        self.reset_idle_timer()


if __name__ == "__main__":
    app = ProtoMillApp()
    app.mainloop()