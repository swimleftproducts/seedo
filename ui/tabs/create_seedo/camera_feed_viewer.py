import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import numpy as np
import timeit

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
        self.last_embedding_time = 0.0

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
                    x1, y1, x2, y2 = region['roi']
                    # apply offset to go from actual image coords to canvas coords
                    x1, y1, x2, y2 = self.parent.remove_roi_offset_and_scale(x1, y1, x2, y2)
                    self.camera_viewer.create_rectangle(x1, y1, x2, y2, outline="red", width=2)

                if timeit.default_timer() - self.last_embedding_time > .1:
                    self.last_embedding_time = timeit.default_timer()
                    for region in self.parent.semantic_regions:
                        x1, y1, x2, y2 = region['roi']
                        # apply offset to go from actual image coords to canvas coords
                        x1, y1, x2, y2 = self.parent.remove_roi_offset_and_scale(x1, y1, x2, y2)
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
                    end = timeit.default_timer()
                    print(f"Similarity display time: {end - self.last_embedding_time:.4f} seconds")
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

 

