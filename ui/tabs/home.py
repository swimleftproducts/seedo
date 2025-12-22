from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
from enum import Enum
import time
import os


class ViewType(Enum):
    PLAIN = 'plain'
    DEPTH = 'depth'


class HomeTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.MenuView = MenuView(self, controller)
        self.CameraViewerView = CameraViewerView(self, controller)

        # stack frames; only the top one is visible
        self.MenuView.grid(row=0, column=0, sticky="nsew")
        self.CameraViewerView.grid(row=0, column=0, sticky="nsew")

        self.current_frame = self.MenuView
        self.MenuView.tkraise()

    def show_frame(self, frame):
        if hasattr(self.current_frame, "on_hide"):
            self.current_frame.on_hide()

        frame.tkraise()

        if hasattr(frame, "on_show"):
            frame.on_show()

        self.current_frame = frame


class CameraViewerView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.view = ViewType.PLAIN
        self._showing_preview = False
        self._after_id = None 

        self.last_depth_ts = 0.0

        self.capture_still = False

        # ---- top bar FIRST so it remains visible ----
        top_bar = tk.Frame(self)
        top_bar.pack(fill="x", side="top")

        ttk.Button(
            top_bar,
            text="Back",
            command=lambda: parent.show_frame(parent.MenuView)
        ).pack(side="left")

        ttk.Button(
            top_bar,
            text="Snap Still",
            command= self.trigger_still_capture
        ).pack(side="top")

        ttk.Button(
            top_bar,
            text="Toggle Depth Map",
            command=self.toggle_view_type
        ).pack(side="right")

        # ---- video label SECOND ----
        self.video_label = tk.Label(self)
        self.video_label.pack(expand=True, fill='both')

    # -----------------------------
    #       View Toggle
    # -----------------------------
    def toggle_view_type(self):
        if self.view == ViewType.PLAIN:
            self.view = ViewType.DEPTH
            self.controller.start_running_depth_map()
        else:
            self.view = ViewType.PLAIN
            self.controller.stop_running_depth_map()

    # -----------------------------
    #       Lifecycle Hooks
    # -----------------------------
    def on_show(self):
        self._showing_preview = True
        self._run_loop()
        if self.view == ViewType.DEPTH:
            self.controller.start_running_depth_map()

    def on_hide(self):
        self._showing_preview = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.controller.stop_running_depth_map()
    
    def trigger_still_capture(self):
        self.capture_still = True

    # -----------------------------
    #       Preview Loop
    # -----------------------------
    def _run_loop(self):
        if not self._showing_preview:
            return

        if self.view == ViewType.PLAIN:
            self.update_preview_plain()
        else:
            self.update_preview_depth_map()

        # schedule next frame
        self._after_id = self.after(33, self._run_loop)

    # -----------------------------
    #       Plain Preview
    # -----------------------------
    def update_preview_plain(self):
        camera = self.controller.camera_manager

        if not camera.active:
            self.video_label.config(image='', text="Camera not running...")
            return

        frame = camera.latest_frame
        if frame is None:
            return

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
        if (self.capture_still):
            h = os.getenv('HEIGHT')
            w = os.getenv('WIDTH')
            img_full = img
            if h and w:
                img_full = img.resize((int(w),int(h)))
            img_full.save('core/data/stills/most_recent_preview.png')
            self.capture_still = False

    def update_preview_depth_map(self):
        

        now = time.time()
        if now - self.last_depth_ts < 2:
            return
        self.last_depth_ts = now
        self.controller.request_depth()
        img = self.controller.get_depth_map_gray_scale()

        if img is None:
            return

        # convert to PIL
        img_pil = Image.fromarray(img)

        if (self.capture_still):
            print('capturing depth map')
            img_pil_full = img_pil
            h = os.getenv('HEIGHT')
            w = os.getenv('WIDTH')
            if h and w:
                print('resizing to', w, h)
                img_pil_full = img_pil.resize((int(w),int(h)))
            img_pil_full.save('core/data/stills/most_recent_depth_map.png')
            self.capture_still = False

        # get current display size
        w = self.video_label.winfo_width()
        h = self.video_label.winfo_height()

        # if width/height are zero (first frame), skip resize
        if w > 1 and h > 1:
            img_pil = img_pil.resize((w, h), Image.NEAREST)

        imgtk = ImageTk.PhotoImage(img_pil)

        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)


class MenuView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.controller = controller

        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(7, weight=3)

        for r in range(1, 7):
            self.rowconfigure(r, weight=1)

        ttk.Button(
            self, style='Standard.TButton', text="View Camera", width=20,
            command=lambda: parent.show_frame(parent.CameraViewerView)
        ).grid(row=2, column=0)

        ttk.Button(
            self, style='Standard.TButton', text="Start Camera", width=20,
            command=self.controller.start_camera
        ).grid(row=3, column=0)

        ttk.Button(
            self, style='Standard.TButton', text="Stop Camera", width=20,
            command=self.controller.stop_camera
        ).grid(row=4, column=0)

        ttk.Button(
            self, style='Standard.TButton', text="Start Recording", width=20,
            command=self.controller.start_recording
        ).grid(row=5, column=0)

        ttk.Button(
            self, style='Standard.TButton', text="Stop Recording", width=20,
            command=self.controller.stop_recording
        ).grid(row=6, column=0)
