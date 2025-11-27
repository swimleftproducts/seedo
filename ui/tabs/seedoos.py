from tkinter import ttk
import tkinter as tk
import time

class SeeDoosOverviewTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.controller = controller

        # Stores UI widgets per seedo for live updating
        self.rows = {}  

        # Column definitions
        self.column_headers = {
            'name': 'SeeDo Name',
            'type': 'Type',
            'interval_sec': 'Evaluation Interval (sec)',
            '_last_action_time': "Last Action Time (timestamp)",
            'enabled': 'Enabled',
            'change_status': 'Enable / Disable'
        }

        self.build_ui()
        self.build_rows()

    # -------------- HEADER UI ----------------
    def build_ui(self):
        seedos = self.controller.seedo_manager.seedos
        num_seedos = len(seedos)

        # Row 0 = header, does not expand vertically
        self.rowconfigure(0, weight=0)

        # Data rows expand
        for r in range(1, num_seedos + 1):
            self.rowconfigure(r, weight=0)

        # Configure columns to expand evenly
        for c in range(len(self.column_headers)):
            self.columnconfigure(c, weight=1)

        # ---- Header tiles ----
        for col_index, (attr, header) in enumerate(self.column_headers.items()):
            tile = tk.Frame(self, bg="black", height=40)
            tile.grid(row=0, column=col_index, padx=10, pady=10, sticky="ew")
            tile.grid_propagate(False)

            label = ttk.Label(tile, text=header, foreground='white', anchor="center",
                              background="black", font=('Arial', 12))
            label.pack(expand=True, fill='both', padx=5, pady=5)

    # -------------- BUILD DATA ROWS ----------------
    def build_rows(self):

        seedos = self.controller.seedo_manager.seedos

        for row_index, seedo in enumerate(seedos, start=1):

            name = ttk.Label(self, anchor='center', relief="solid", text=seedo.name)
            name.grid(row=row_index, column=0, sticky="nsew", padx=5, pady=5)

            type_label = ttk.Label(self, anchor='center', relief="solid", text=type(seedo).__name__)
            type_label.grid(row=row_index, column=1, sticky="nsew", padx=5, pady=5)

            interval = ttk.Label(self, anchor='center', relief="solid")
            interval.grid(row=row_index, column=2, sticky="nsew", padx=5, pady=5)

            last_action = ttk.Label(self, anchor='center', relief="solid")
            last_action.grid(row=row_index, column=3, sticky="nsew", padx=5, pady=5)

            enabled = ttk.Label(self, anchor='center', relief="solid")
            enabled.grid(row=row_index, column=4, sticky="nsew", padx=5, pady=5)

            start_or_stop_style = "Red.TButton" if seedo.enabled else "Green.TButton"
            start_or_stop = ttk.Button(
                self, 
                style=start_or_stop_style,
                text=('stop' if seedo.enabled else 'start'),
                command=lambda s=seedo: self.controller.toggle_seedo(s.name),
            )
            start_or_stop.grid(row=row_index, column=5, sticky="nsew", padx=5, pady=5)
            

            # store in dictionary for refresh
            self.rows[seedo] = (interval, last_action, enabled, start_or_stop)

        # Initial refresh so data is visible immediately
        self.refresh()

    # -------------- REFRESH DATA ----------------
    def refresh(self):
        """Refresh UI row values from current SeeDo state."""
        for seedo, widgets in self.rows.items():
            interval, last_action, enabled, start_or_stop = widgets

            enabled.config(text="Yes" if seedo.enabled else "No")
            interval.config(text=f"{seedo.interval_sec:.1f}")
            # convert timestamp to readable format using time module
            last_action_time = seedo._last_action_time
            last_action_time_str_hours_mins_secs = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_action_time)) if last_action_time > 0 else "Never"
            last_action.config(text=last_action_time_str_hours_mins_secs  )
        
            #update button text:
            start_or_stop.config(
                text=('stop' if seedo.enabled else 'start'),
                style=("Red.TButton" if seedo.enabled else "Green.TButton")
            )

         
