from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
import time


class HomeTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

   
        self.MenuView = MenuView(self,controller)
        self.CameraViewerView = CameraViewerView(self,controller)

        # stack frames on top of each other
        self.MenuView.grid(row=0, column=0, sticky="nsew")
        self.CameraViewerView.grid(row=0, column=0, sticky="nsew")

        self.MenuView.tkraise()  # start on page 1



    def show_frame(self, frame):
        frame.tkraise()

class CameraViewerView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.video_label = tk.Label(self)
        self.video_label.pack(expand=True, fill='both')

        self.back_button =  ttk.Button(self, text="Back", width=20,
                   command=lambda: parent.show_frame(parent.MenuView)).place(anchor='nw')

        self.update_preview()
        
    def update_preview(self):
            camera = self.controller.camera_manager

            if not camera.active:
                self.video_label.config(image='', text="Camera not running...")
            else:

                frame = camera.latest_frame

                if frame is not None:
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)

            self.after(33, self.update_preview)   



class MenuView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.controller = controller

        # one column that expands
        self.columnconfigure(0, weight=1)

        # spacer rows top & bottom absorb available space
        self.rowconfigure(0, weight=1)  
        self.rowconfigure(7, weight=3)

        # button rows have minimal expansion
        for r in range(1, 7):
            self.rowconfigure(r, weight=1)

        ttk.Button(self, style='Standard.TButton', text="Create SeeDo", width=20,).grid(row=1, column=0,  sticky="")
        ttk.Button(self, style='Standard.TButton', text="View Camera", width=20,
                   command=lambda: parent.show_frame(parent.CameraViewerView)).grid(row=2, column=0, sticky="")
        ttk.Button(self, style='Standard.TButton', text="Start Camera",
                   width=20, command=self.controller.start_camera).grid(row=3, column=0, sticky="")
        ttk.Button(self, style='Standard.TButton', text="Stop Camera",
                   width=20, command=self.controller.stop_camera).grid(row=4, column=0, sticky="")
        ttk.Button(self, style='Standard.TButton', text="Start Recording",
                   width=20, command=self.controller.start_recording).grid(row=5, column=0, sticky="")
        ttk.Button(self, style='Standard.TButton', text="Stop Recording",
                   width=20, command=self.controller.stop_recording).grid(row=6, column=0, sticky="")
