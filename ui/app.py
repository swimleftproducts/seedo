import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from ui.tabs.seedoos import SeeDoosOverviewTab
from ui.tabs.create_seedo import CreateSeeDo
from ui.tabs.home import HomeTab


class SeeDoApp(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.title("SeeDo Prototype")
        self.controller = controller

        self.geometry("920x700")

        self.showing_camera = False

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tabs
        self.home_tab = HomeTab(self.notebook, self.controller)
        self.running_tab = SeeDoosOverviewTab(self.notebook, self.controller)
        self.paused_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        self.create_seedo = CreateSeeDo(self.notebook, self.controller)

        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.running_tab, text="SeeDos Overview")
        self.notebook.add(self.config_tab, text="Config")
        self.notebook.add(self.create_seedo, text="Create SeeDo")

        # update UI fixes
        self.notebook.bind("<<NotebookTabChanged>>",
                           lambda event: self.update_idletasks())
        # start heartbeat tick
        self.tick()

        #start UI refresh loop
        self.refresh_ui()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- TICK LOOP ----------------
    def tick(self):
        """Master tick function. UI drives time, controller performs work."""
        self.controller.tick()
        self.after(10, self.tick)      # ~30 FPS engine tick

    def refresh_ui(self):
        self.running_tab.refresh()
        self.after(500, self.refresh_ui)  # refresh every second

    # ---------------- CLEANUP ----------------
    def on_close(self):
        print("Shutting down...")
        self.controller.shutdown()
        self.destroy()


