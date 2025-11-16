import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Notebook Example")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

frame1 = tk.Frame(notebook, bg="lightblue")
frame2 = tk.Frame(notebook, bg="lightgreen")

notebook.add(frame1, text="Home")
notebook.add(frame2, text="Settings")

tk.Label(frame1, text="Home Content").pack(padx=20, pady=20)
tk.Label(frame2, text="Settings Content").pack(padx=20, pady=20)

root.mainloop()
