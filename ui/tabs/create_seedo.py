import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import numpy as np


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
        self.controller = controller

        self.camera_viewer_width = 500
        self.camera_viewer_height = 350

        self.roi_padding_offset: tuple = self.roi_padding_offset()
        print("ROI padding offset:", self.roi_padding_offset)

        self.roi_scaling_factor: tuple = self.calculate_roi_scaling_factor()
        print("ROI scaling factor:", self.roi_scaling_factor)

        #
        self.semantic_regions = []
        # Each item will have the format
        #  {
        #   roi: tuple (x1, y1, x2, y2) in captured image coords
        #   embedding: np.ndarray | None = None,
        #   image: Image.Image | None = None
        #   label: str | None = None
        #   color: str = "red"
        # }

        # set up grid with 4 columns and 7 rows
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=4, uniform="col")
        
        self.rowconfigure(0, weight=0, uniform="row")
        self.rowconfigure(1, weight=20, uniform="row")
        self.rowconfigure(2, weight=0, uniform="row")

        title = tk.Label(
            self,
            text="Semantic Similarity SeeDo Creation",
            foreground='black',
            background='lightblue',
            font=('Arial', 18, 'bold')
        )
        title.grid(row=0, column=0, columnspan=2, pady=5)

        camera_feed = CameraFeedViewer(
            self, 
            controller, 
            self.camera_viewer_width, 
            self.camera_viewer_height
        )
        camera_feed.grid(row=1, column=1, sticky="nsew")

        tk.Button(
            self,
            text="Back",
            font=('Arial', 16),
            command=lambda: self.parent.show_frame(self.parent.frame_1)
        ).grid(row=3, column=0, columnspan=2, pady=20)
    
    def roi_padding_offset(self):
            """Calculate padding offset for ROI selection based on camera viewer size and
            actual image size."""
            camera = self.controller.camera_manager
            # Get actual camera resolution
            actual_width = camera.target_width
            actual_height = camera.target_height

            # calculate padding offset on top based on image size and resized image
            # aspect ratios
            aspect_ratio_image = actual_width / actual_height
            aspect_ratio_viewer = self.camera_viewer_width / self.camera_viewer_height

            if aspect_ratio_image > aspect_ratio_viewer:
                # image is wider than viewer, so padding on top and bottom
                scaled_height = self.camera_viewer_width / aspect_ratio_image
                pad_y = (self.camera_viewer_height - scaled_height) / 2
                pad_x = 0

            else:
                # image is taller than viewer, so padding on sides
                scaled_width = self.camera_viewer_height * aspect_ratio_image
                pad_x = (self.camera_viewer_width - scaled_width) / 2
                pad_y = 0

            pad_x = max(round(pad_x), 0)
            pad_y = max(round(pad_y), 0)
            
            return pad_x, pad_y
    
    def calculate_roi_scaling_factor(self):
        """Calculate scaling factor for ROI selection based on camera viewer size and
        actual image size."""
        camera = self.controller.camera_manager
        # Get actual camera resolution
        actual_width = camera.target_width
        actual_height = camera.target_height

        scale_x = actual_width / (self.camera_viewer_width - 2 * self.roi_padding_offset[0])
        scale_y = actual_height / (self.camera_viewer_height - 2 * self.roi_padding_offset[1])

        return scale_x, scale_y

    def capture_embeddings(self):
        #TODO need to remove direct use of camera manger.
        camera = self.controller.camera_manager
        
        if not camera.active:
            print("Camera not active, cannot capture embeddings.")
            return
        latest_frame = camera.latest_frame
        if latest_frame is None:
            print("No frame available from camera.")
            return
        images = []
        for region in self.semantic_regions:
            roi = region['roi']
            img = Image.fromarray(latest_frame)
            img = self.get_image_from_frame(img, roi)
            region['image'] = img
            images.append(img)
            #TODO need to remove direct call to ml_manager from here
        embeddings = self.controller.ml_manager.mobile_net_v3.get_embedding_batch(images)
        for region, embedding in zip(self.semantic_regions, embeddings):
            region['embedding'] = embedding
            
    def get_image_from_frame(self, frame, roi):
        x1, y1, x2, y2 = roi
        return frame.crop((x1, y1, x2, y2))
    
    def apply_roi_offset_and_scale(self, x1, y1, x2, y2):
        """go from canvas coords to actual image coords"""
        pad_x, pad_y = self.roi_padding_offset
        scale_x, scale_y = self.roi_scaling_factor
        return (round((x1 - pad_x) * scale_x), 
                round((y1 - pad_y) * scale_y), 
                round((x2 - pad_x) * scale_x), 
                round((y2 - pad_y) * scale_y))
    
    def remove_roi_offset_and_scale(self, x1, y1, x2, y2):
        """go from actual image coords to canvas coords"""
        pad_x, pad_y = self.roi_padding_offset
        scale_x, scale_y = self.roi_scaling_factor
        return (round(x1 / scale_x + pad_x), 
                round(y1 / scale_y + pad_y), 
                round(x2 / scale_x + pad_x), 
                round(y2 / scale_y + pad_y))
    
class CameraFeedViewer(tk.Frame):
    def __init__(self, parent, controller, width, height):
        super().__init__(parent, background='lightblue')
        self.parent = parent
        self.controller = controller

        self.width = width
        self.height = height

        self.start_x = None
        self.start_y = None
        self.rect = None 

        self.show_similarities = False

        self.columnconfigure(0, weight=1, uniform="col")
        
        self.rowconfigure(0, weight=0, )
        self.rowconfigure(1, weight=10, uniform="row")
        self.rowconfigure(2, weight=0, )
        self.rowconfigure(3, weight=0)

        self.config(width=width, height=height)
        self.grid_propagate(False)
   

        title = tk.Label(
            self,
            text="Select ROI box with mouse clicks, press s to save",
            foreground='black',
            background='lightblue',
            font=('Arial', 14, 'bold')
        )
        title.grid(row=0, column=0, pady=5)
        
        #NOTE: -5 is just to hide a sliver of bg. Not sure why the image width does not
        # match canvas width exactly. Maybe investigate later.
        self.camera_viewer = tk.Canvas(
            self, 
            width=self.width, 
            height=self.height, 
            cursor="cross",
            bg="lightblue",
            border=0,
            borderwidth=0,
            highlightthickness=0
        )
        self.camera_viewer.grid(row=1, column=0)

        self.capture_embeddings = ttk.Button(
            self,
            text='Capture Embeddings',
            style='Standard.TButton',
            command=self.parent.capture_embeddings
        )
        self.capture_embeddings.grid(row=2, column=0, pady=10, padx=10)
        self.show_similarities = ttk.Button(
            self,
            text='Show similarity',
            style='Standard.TButton',
            command= self.toggle_show_similarities,
        )
        self.show_similarities.grid(row=3, column=0, pady=10, padx=10)

        

        self.camera_viewer.bind("<ButtonPress-1>", self.on_mouse_down)
        self.camera_viewer.bind("<B1-Motion>", self.on_mouse_drag)
        self.camera_viewer.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.camera_viewer.bind("<BackSpace>", self.delete_last_roi)

        #not sure if this will work as expected if used mouses out of canvas area
        #self.bind("s", self.save_rois)

        self.update_camera_viewer()

    def update_camera_viewer(self):
            #NOTE: need to remove direct use of camera manger
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

                for region in self.parent.semantic_regions:
                    print('Drawing ROI:', region['roi'])
                    x1, y1, x2, y2 = region['roi']
                    # apply offset to go from actual image coords to canvas coords
                    x1, y1, x2, y2 = self.parent.remove_roi_offset_and_scale(x1, y1, x2, y2)
                    print('Drawing ROI (canvas coords):', (x1, y1, x2, y2))
                    self.camera_viewer.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
                    if self.show_similarities and region['embedding'] is not None:
                        # get current frame sliced from the ROI
                        # get embedding of the new sliced image
                        # compare to existing embedding
                        # show similarity score
                        current_img = self.parent.get_image_from_frame(img, (x1, y1, x2, y2))
                        current_img.save("debug_current_roi.png")
                        region['image'].save("debug_region_roi.png")
                        current_embedding = self.controller.ml_manager.mobile_net_v3.get_image_embedding(current_img)
                        sim = self.controller.ml_manager.mobile_net_v3.cosine_similarity_matrix(
                            np.vstack([region['embedding'].squeeze(), current_embedding.squeeze()])
                        )
                        similarity_score = sim[0,1]
                        self.camera_viewer.create_text(
                            (x1 + x2) // 2,
                            y2 + 15,
                            text=f"Sim: {similarity_score:.2f}",
                            fill="yellow",
                            font=("Helvetica", 12)
                        )
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
        x1, y1, x2, y2 = self.parent.apply_roi_offset_and_scale(x1, y1, x2, y2)
        self.parent.semantic_regions.append({
            'roi':(x1, y1, x2, y2),
            'embedding': None,
            'label': None,
            'color': "red"
        })
        self.rect = None
    
    def delete_last_roi(self, event=None):
        if self.parent.semantic_regions:
            self.parent.semantic_regions.pop()
            self.rect = None    
        return
    
    def toggle_show_similarities(self):
        self.show_similarities = not self.show_similarities

 

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

