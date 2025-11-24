import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import numpy as np  
from .camera_feed_viewer import CameraFeedViewer
from .semantic_similarity_options import SemanticSimilarityOptions

class CreateSeeDo_Semantic_Similarity_Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.parent = parent
        self.controller = controller

        self.camera_viewer_width = 500
        self.camera_viewer_height = 350

        self.roi_padding_offset: tuple = self.roi_padding_offset()
        self.roi_scaling_factor: tuple = self.calculate_roi_scaling_factor()

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
        self.columnconfigure(0, weight=2, uniform="col")
        self.columnconfigure(1, weight=3, uniform="col")
        
        self.rowconfigure(0, weight=0, uniform="row")
        self.rowconfigure(1, weight=20, uniform="row")
        self.rowconfigure(2, weight=5, uniform="row")

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


        self.semantic_options = SemanticSimilarityOptions(self, controller)
        self.semantic_options.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)


        self.back = ttk.Button(
            self,
            text='Back',
            style='Standard.TButton',
            command=lambda: self.parent.show_frame(self.parent.frame_1)
        ).place (x=10, y=10, anchor="nw")

        self.create_seedo_button = ttk.Button(
            self,
            text='Create SeeDo',
            style='Green.TButton',
            command=self.save   
        )
        self.create_seedo_button.grid(row=2, column=1)

    def save(self):
        options_data = self.semantic_options.build_option_payload()
        print("options to save:", options_data)
        pass

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
    