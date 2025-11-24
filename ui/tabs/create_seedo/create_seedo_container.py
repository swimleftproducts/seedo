import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import numpy as np
from .semantic_similarity_frame import CreateSeeDo_Semantic_Similarity_Frame
from .create_seedo import CreateSeeDo_Frame

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


