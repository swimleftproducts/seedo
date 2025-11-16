import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from camera_manager.camera_manager import CameraManager


class SeeDoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SeeDo Prototype")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
          "Back.TButton",
          padding=0,
          relief="flat",
          borderwidth=0
        )


        self.geometry("900x500")

        self.showing_camera = False   

        # camera manager
        self.camera_manager = CameraManager()

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tabs
        self.home_tab = ttk.Frame(self.notebook)
        self.running_tab = ttk.Frame(self.notebook)
        self.paused_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.running_tab, text="Running SeeDos")
        self.notebook.add(self.paused_tab, text="Paused SeeDos")
        self.notebook.add(self.config_tab, text="Config")

        # Listen for any tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Build pages once
        self.build_home_page()
        self.build_camera_page()

        self.show_home()

    # ---------------- HOME PAGE ----------------
    def build_home_page(self):
        self.home_page = tk.Frame(self.home_tab)
        ttk.Button(self.home_page, text="Create SeeDo", width=20).pack(pady=20)
        ttk.Button(self.home_page, text="View Camera", width=20,
                   command=self.show_camera_page).pack(pady=20)

    # ---------------- CAMERA PAGE ----------------
    def build_camera_page(self):
        self.camera_page = tk.Frame(self.home_tab)
        self.video_label = tk.Label(self.camera_page)
        self.video_label.pack(pady=10)

        ttk.Button(self.camera_page, text="Back",
                   command=self.show_home, style="Back.TButton").place(x=10, y=10)

    # ---------------- CAMERA UPDATE LOOP ----------------
    def update_camera_view(self):
        if not self.showing_camera:
            return  # stop updating if not in camera mode

        self.camera_manager.capture_frame()
        frame = self.camera_manager.get_frame()

        if frame is not None:
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.after(66, self.update_camera_view)

    # ---------------- NAVIGATION ----------------
    def show_camera_page(self):
        self.showing_camera = True
        self.home_page.pack_forget()
        self.camera_page.pack(expand=True, fill="both")
        self.update_camera_view()

    def show_home(self):
        self.showing_camera = False
        self.camera_page.pack_forget()
        self.home_page.pack(expand=True, fill="both")

    def on_tab_change(self, event):
        """Stop camera if user navigates to another tab."""
        self.showing_camera = False
        self.camera_page.pack_forget()
        self.home_page.pack(expand=True, fill="both")


    def on_close(self):
        self.showing_camera = False
        self.camera_manager.release()
        self.destroy()


if __name__ == "__main__":
    app = SeeDoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
