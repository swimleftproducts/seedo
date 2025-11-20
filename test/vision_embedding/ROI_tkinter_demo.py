import tkinter as tk
import cv2
from PIL import Image, ImageTk
import time
import torch.nn.functional as F
import numpy as np

from MobileNet_run import get_embedding   # same directory


class ROIDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("ROI + Similarity Demo")

        self.cap = cv2.VideoCapture(0)
        self.width = 640
        self.height = 480

        self.rois = []
        self.start_x = None
        self.start_y = None
        self.rect = None

        self.baseline_embedding = None
        self.last_eval_time = time.time()
        self.threshold = 0.70
        self.found_text = None

        self.canvas = tk.Canvas(
            root, width=self.width, height=self.height,
            cursor="cross", bg="black"
        )
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("c", self.capture_baseline)

        self.score_text = self.canvas.create_text(
            10, 20, anchor="nw", fill="white",
            text="Score: ---", font=("Helvetica", 14)
        )

        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_frame)
            return

        # convert and resize
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.width, self.height))
        self.current_frame = frame

        # convert to Tk image
        img = Image.fromarray(frame)
        self.photo = ImageTk.PhotoImage(image=img)

        # draw frame (delete old first); keep frame at bottom
        self.canvas.delete("frame")
        self.canvas.create_image(
            0, 0, anchor=tk.NW, image=self.photo, tags="frame"
        )
        self.canvas.tag_lower("frame")

        # clear old ROIs and redraw
        self.canvas.delete("roi")
        self.canvas.delete("active_roi")

        for (x1, y1, x2, y2) in self.rois:
            self.canvas.create_rectangle(
                x1, y1, x2, y2, outline="red", width=2, tags="roi"
            )

        if self.rect:
            self.canvas.create_rectangle(
                *self.rect, outline="yellow", width=2, tags="active_roi"
            )

        # keep texts on top
        self.canvas.tag_raise(self.score_text)
        if self.found_text is not None:
            self.canvas.tag_raise(self.found_text)

        # check similarity every 5 seconds
        if (
            self.baseline_embedding is not None
            and (time.time() - self.last_eval_time) > 1
        ):
            self.last_eval_time = time.time()
            self.evaluate_similarity()

        self.root.after(30, self.update_frame)

    def evaluate_similarity(self):
        if not self.rois:
            return

        x1, y1, x2, y2 = self.rois[0]
        roi = self.current_frame[y1:y2, x1:x2]

        if roi.size == 0:
            print("ROI empty — drag properly and press C again")
            return

        pil = Image.fromarray(roi).convert("RGB")
        emb = get_embedding(pil)

        score = float(F.cosine_similarity(self.baseline_embedding, emb, dim=0))
        print(f"Similarity score: {score:.3f}")

        self.canvas.itemconfig(self.score_text, text=f"Score: {score:.3f}")

        # show NOT FOUND when below threshold, FOUND otherwise
        if score < self.threshold:
            # NOT FOUND
            if self.found_text is not None:
                self.canvas.delete(self.found_text)
            self.found_text = self.canvas.create_text(
                self.width // 2,
                self.height // 2,
                text="NOT FOUND",
                fill="red",
                font=("Helvetica", 32, "bold"),
            )
        else:
            if self.found_text is not None:
                self.canvas.delete(self.found_text)
            self.found_text = self.canvas.create_text(
                self.width // 2,
                self.height // 2,
                text="FOUND",
                fill="green",
                font=("Helvetica", 32, "bold"),
            )

    def on_mouse_down(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = None

    def on_mouse_drag(self, event):
        self.rect = (self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        x1, x2 = sorted([self.start_x, event.x])
        y1, y2 = sorted([self.start_y, event.y])
        self.rois = [(x1, y1, x2, y2)]
        self.rect = None
        print("ROI:", self.rois[0])

    def capture_baseline(self, event=None):
        if not self.rois:
            print("No ROI selected")
            return

        x1, y1, x2, y2 = self.rois[0]
        roi = self.current_frame[y1:y2, x1:x2]

        print("ROI shape on capture:", roi.shape)

        if roi.size == 0:
            print("ERROR: ROI empty — draw larger rectangle")
            return

        pil = Image.fromarray(roi).convert("RGB")
        emb = get_embedding(pil)

        print("Embedding returned?", emb is not None)
        print("Embedding shape:", emb.shape if emb is not None else None)

        self.baseline_embedding = emb
        self.last_eval_time = time.time()
        print("Baseline captured!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ROIDrawer(root)
    root.mainloop()
