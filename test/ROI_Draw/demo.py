"""
    Demo script for drawing ROIs on webcam feed using Tkinter.
    Click and drag to draw rectangles. Press 's' to save ROIs to a file
"""

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

class ROIDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("ROI Selection Example")

        self.cap = cv2.VideoCapture(0)  # webcam
        self.rois = []  # list of (x1, y1, x2, y2)

        self.start_x = None
        self.start_y = None
        self.rect = None  # temporary active rectangle

        self.canvas = tk.Canvas(root, width=640, height=480, cursor="cross")
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("s", self.save_rois)

        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_frame)
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.current_frame = frame

        img = Image.fromarray(frame)
        self.photo = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # draw saved ROIs
        for (x1, y1, x2, y2) in self.rois:
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)

        # draw active rectangle
        if self.rect:
            self.canvas.create_rectangle(self.rect, outline="yellow", width=2)

        self.root.after(30, self.update_frame)

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = None

    def on_mouse_drag(self, event):
        self.rect = (self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        end_x, end_y = event.x, event.y
        self.rois.append((self.start_x, self.start_y, end_x, end_y))
        self.rect = None

    def save_rois(self, event=None):
        print("Saved ROIs:", self.rois)
        # Example: Save to file
        import json
        with open("test/ROI_draw/rois.json", "w") as f:
            json.dump(self.rois, f)
        print("ROIs written to rois.json")

if __name__ == "__main__":
    root = tk.Tk()
    app = ROIDrawer(root)
    root.mainloop()
