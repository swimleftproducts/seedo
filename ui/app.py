import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from ui.tabs.running_tab import RunningTab


class SeeDoApp(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.title("SeeDo Prototype")
        self.controller = controller

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Back.TButton",
            padding=0,
            relief="flat",
            borderwidth=0
        )

        self.geometry("920x700")

        self.showing_camera = False

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tabs
        self.home_tab = ttk.Frame(self.notebook)
        self.running_tab = RunningTab(self.notebook, self.controller)
        self.paused_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.running_tab, text="Running SeeDos")
        self.notebook.add(self.paused_tab, text="Paused SeeDos")
        self.notebook.add(self.config_tab, text="Config")

        self.build_home_page()
        self.build_camera_page()
        self.show_home()

        # update UI fixes
        self.notebook.bind("<<NotebookTabChanged>>",
                           lambda event: self.update_idletasks())

        # start heartbeat tick
        self.tick()

        #start UI refresh loop
        self.refresh_ui()

        self.protocol("WM_DELETE_WINDOW", self.on_close)


    # ---------------- TICK LOOP ----------------
    def tick(self):
        """Master tick function. UI drives time, controller performs work."""
        self.controller.tick()
        self.after(10, self.tick)      # ~30 FPS engine tick

    def refresh_ui(self):
        self.running_tab.refresh()
        self.after(1000, self.refresh_ui)  # refresh every second

    # ---------------- HOME PAGE ----------------
    def build_home_page(self):
        self.home_page = tk.Frame(self.home_tab)

        ttk.Button(self.home_page, text="Create SeeDo", width=20).pack(pady=20)

        ttk.Button(self.home_page, text="View Camera", width=20,
                   command=self.show_camera_page).pack(pady=20)

        ttk.Button(self.home_page, text="Start Camera",
                   width=20, command=self.controller.start_camera).pack(pady=20)

        ttk.Button(self.home_page, text="Stop Camera",
                   width=20, command=self.controller.stop_camera).pack(pady=10)

        ttk.Button(self.home_page, text="Start Recording",
                   width=20, command=self.controller.start_recording).pack(pady=10)

        ttk.Button(self.home_page, text="Stop Recording",
                   width=20, command=self.controller.stop_recording).pack(pady=10)


    # ---------------- CAMERA PREVIEW PAGE ----------------
    def build_camera_page(self):
        self.camera_page = tk.Frame(self.home_tab)
        self.video_label = tk.Label(self.camera_page)
        self.video_label.pack(pady=10)

        ttk.Button(
            self.camera_page,
            text="Back",
            command=self.show_home,
            style="Back.TButton"
        ).place(x=10, y=10)


    def update_preview(self):
        camera = self.controller.camera_manager

        if not camera.active:
            self.video_label.config(image='', text="Camera not running...")
            return

        frame = camera.latest_frame

        if frame is not None:
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.after(66, self.update_preview)    # ~15 FPS preview refresh


    # ---------------- NAVIGATION ----------------
    def show_camera_page(self):
        self.showing_camera = True
        self.home_page.pack_forget()
        self.camera_page.pack(expand=True, fill="both")
        self.update_preview()

    def show_home(self):
        self.showing_camera = False
        self.camera_page.pack_forget()
        self.home_page.pack(expand=True, fill="both")


    # ---------------- CLEANUP ----------------
    def on_close(self):
        print("Shutting down...")
        self.controller.shutdown()
        self.destroy()


