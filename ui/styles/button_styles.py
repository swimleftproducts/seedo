from tkinter import ttk

def setup_button_styles():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("standard.TButton", relief="flat", borderwidth=0, padding=10,
                    background="#6e6d78", foreground="white", focusthickness=0)

    style.map("Menu.TButton",
              background=[("active", "#82818c"), ("pressed", "#585762")],
              relief=[("pressed", "flat"), ("active", "flat")])
