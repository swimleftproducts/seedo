import tkinter as tk
from tkinter import ttk

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

