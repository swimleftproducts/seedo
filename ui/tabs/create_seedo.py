import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps


class CreateSeeDo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        #
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # pass controller (self) to frames
        self.frame_1 = CreateSeeDo_Frame(self)
        self.frame_2 = CreateSeeDo_Semantic_Similarity_Frame(self, controller)

        # stack frames on top of each other
        self.frame_1.grid(row=0, column=0, sticky="nsew")
        self.frame_2.grid(row=0, column=0, sticky="nsew")

        self.frame_1.tkraise()  # start on page 1

    def show_frame(self, frame):
        frame.tkraise()


class CreateSeeDo_Semantic_Similarity_Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.parent = parent

        # set up grid with 4 columns and 7 rows
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")
        
        self.rowconfigure(0, weight=0, uniform="row")
        self.rowconfigure(1, weight=5, uniform="row")
        self.rowconfigure(2, weight=0, uniform="row")

        title = tk.Label(
            self,
            text="Semantic Similarity SeeDo creation",
            foreground='black',
            background='lightblue',
            font=('Arial', 24, 'bold')
        )
        title.grid(row=0, column=0, columnspan=2, pady=10)

        camera_feed = CameraFeedViewer(self, controller)
        camera_feed.grid(row=1, column=1)

        tk.Button(
            self,
            text="Back",
            font=('Arial', 16),
            command=lambda: self.parent.show_frame(self.parent.frame_1)
        ).grid(row=3, column=0, columnspan=2, pady=20)


class CameraFeedViewer(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.controller = controller
        self.rois = []  # list of (x1, y1, x2, y2)

        self.width = 400
        self.height = 300

        self.start_x = None
        self.start_y = None
        self.rect = None 

        self.columnconfigure(0, weight=1, uniform="col")
        
        self.rowconfigure(0, weight=0, )
        self.rowconfigure(1, weight=10, uniform="row")
        self.rowconfigure(2, weight=0, )

        title = tk.Label(
            self,
            text="Select ROI box with mouse clicks, press s to save",
            foreground='black',
            background='lightblue',
            font=('Arial', 14, 'bold')
        )
        title.grid(row=0, column=0, pady=10)

        self.camera_viewer = tk.Canvas(self, width=self.width, height=self.height, cursor="cross")
        self.camera_viewer.grid(row=1, column=0)

        self.camera_viewer.bind("<ButtonPress-1>", self.on_mouse_down)
        self.camera_viewer.bind("<B1-Motion>", self.on_mouse_drag)
        self.camera_viewer.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.camera_viewer.bind("<BackSpace>", self.delete_last_roi)

        #not sure if this will work as expected if used mouses out of canvas area
        #self.bind("s", self.save_rois)

        self.update_camera_viewer()

    def update_camera_viewer(self):
            camera = self.controller.camera_manager

            if not camera.active:
                self.camera_viewer.create_text(
                    self.width // 2,
                    self.height // 2,
                    text="Camera not running...",
                    font=("Helvetica", 18),
                    tags='camera_off'
                )
            else:
                frame = camera.latest_frame
                if frame is not None:
                    img = Image.fromarray(frame)
                    img = ImageOps.pad(img, (self.width, self.height), color="black")
                    self.imgtk = ImageTk.PhotoImage(image=img)
                    self.camera_viewer.delete("all")
                    self.camera_viewer.create_image(0,0,anchor=tk.NW,image = self.imgtk, tags='frame')
                    self.camera_viewer.tag_raise("frame")

                for (x1, y1, x2, y2) in self.rois:
                    self.camera_viewer.create_rectangle(x1, y1, x2, y2, outline="red", width=2)

                if self.rect:
                    self.camera_viewer.create_rectangle(self.rect, outline="yellow", width=2)
            
            
            
            self.after(33, self.update_camera_viewer)
    
    def on_mouse_down(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = None

    def on_mouse_drag(self, event):
        self.camera_viewer.focus_set()   
        self.rect = (self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        x1, x2 = sorted([self.start_x, event.x])
        y1, y2 = sorted([self.start_y, event.y])
        self.rois.append((x1, y1, x2, y2))
        self.rect = None
    
    def delete_last_roi(self, event=None):
        if self.rois:
            self.rois.pop()
            self.camera_viewer.delete("all")  
            self.rect = None    
        return

 

class CreateSeeDo_Frame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, background="lightblue")
        self.parent = parent

        # set up grid with 4 columns and 7 rows
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=2, uniform="col")
        self.columnconfigure(2, weight=2, uniform="col")
        self.columnconfigure(3, weight=1, uniform="col")
        self.rowconfigure(0, weight=0, uniform="col")
        self.rowconfigure(1, weight=0, uniform="col")
        self.rowconfigure(2, weight=0, uniform="col")
        self.rowconfigure(3, weight=0, uniform="col")

        title = tk.Label(
            self,
            text="Create a New SeeDo",
            foreground='black',
            background='lightblue',
            font=('Arial', 24, 'bold')
        )
        title.grid(row=0, column=0, columnspan=4, pady=10)

        button1 = ttk.Button(
            self,
            text='Semantic Similarity',
            style='Standard.TButton',
            command=lambda: self.parent.show_frame(self.parent.frame_2)
        )
        button1.grid(row=1, column=1, columnspan=2, sticky='nsew', pady=10, padx=10)

        button2 = ttk.Button(
            self,
            text='Pixel Change Detection',
            style='Standard.TButton',
        )
        button2.grid(row=2, column=1,columnspan=2, sticky='nsew', pady=10, padx=10)

        button3 = ttk.Button(
            self,
            text='LLM Action Trigger',
            style='Standard.TButton',
        )
        button3.grid(row=3, column=1, columnspan=2, sticky='nsew', pady=10, padx=10)

