import tkinter as tk
from tkinter import ttk


class SemanticSimilarityOptions(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, background='lightblue')
        self.parent = parent
        self.controller = controller

        # set up grid with 2 columns and 6 rows
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")

        self.rowconfigure(0, weight=1, uniform="row")
        self.rowconfigure(1, weight=1, uniform="row")
        self.rowconfigure(2, weight=1, uniform="row")
        self.rowconfigure(3, weight=1, uniform="row")
        self.rowconfigure(4, weight=1, uniform="row")
        self.rowconfigure(5, weight=1, uniform="row") 
        self.rowconfigure(6, weight=1, uniform="row")

        self.name_label = tk.Label(
            self,
            text="SeeDo Name:",
            foreground='black',
            background='lightblue',
            font=('Arial', 14)
        )
        self.name_label.grid(row=0, column=0, sticky='w', padx=2, pady=2)
        self.name_input = ttk.Entry(self)
        self.name_input.grid(row=0, column=1, sticky='ew')


        self.similarity_threshold_label = tk.Label(
            self,
            text="Similarity Threshold\n (0.0 - 1.0):",
            foreground='black',
            background='lightblue',
            font=('Arial', 14)
        )
        self.similarity_threshold_label.grid(row=1, column=0, sticky='w', padx=2, pady=2)
        self.similarity_threshold_input = ttk.Entry(self)
        self.similarity_threshold_input.insert(0, "0.7")
        self.similarity_threshold_input.grid(row=1, column=1, sticky='ew') 

        self.greater_less_label = tk.Label(
            self,
            text="Trigger When:\n",
            foreground='black',
            background='lightblue',
            font=('Arial', 14),            
        )
        self.greater_less_label.grid(row=2, column=0, sticky='w', padx=2, pady=2)
        self.greater_less_var = tk.StringVar(value="greater")
        self.greater_radio = tk.Radiobutton(
            self,
            text=" Greater Than Threshold",
            variable=self.greater_less_var,
            value="greater",
            background='lightblue',
            foreground='black',
        )
        self.greater_radio.grid(row=2, column=1, sticky='ew')
        self.less_radio = tk.Radiobutton(
            self,
            text="Less Than Threshold",
            variable=self.greater_less_var,
            value="less",
            background='lightblue',
            foreground='black',
        )
        self.less_radio.grid(row=3, column=1, sticky='ew') 

        self.action_type_label = tk.Label(
            self,
            text="Action Type:",
            foreground='black',
            background='lightblue',
            font=('Arial', 14)
        )
        self.action_type_label.grid(row=4, column=0, sticky='w', padx=2, pady=2)
        self.action_type_var = tk.StringVar()
        self.action_type_combo = ttk.Combobox(
            self,
            textvariable=self.action_type_var,
            values=["Email", "TBD"],
            state="readonly",
            style='LightBlue.TCombobox'
        )
        self.action_type_combo.grid(row=4, column=1, sticky='ew')
        self.action_type_combo.bind("<<ComboboxSelected>>", self.on_action_type_change)


        self.email_to_label = tk.Label(
            self,
            text="Email To:",
            foreground='black',
            background='lightblue',
            font=('Arial', 14)
        )
        self.email_to_label.grid(row=5, column=0, sticky='w', padx=2, pady=2)
        self.email_to_input = ttk.Entry(self)
        self.email_to_input.grid(row=5, column=1, sticky='ew')
        self.email_body_input = ttk.Entry(self)

        #need to force multi-line entry box
        self.email_body_label = tk.Label(
            self,
            text="Email Body:",
            foreground='black',
            background='lightblue',
            font=('Arial', 14)
        )
        self.email_body_label.grid(row=6, column=0, sticky='w', padx=2, pady=2)
        self.email_body_input = tk.Text(self, height=5, wrap='word')
        self.email_body_input.grid(row=6, column=1  , sticky='ew')

        self.hide_email_fields()

    def build_option_payload(self):
        payload = {
            "name": self.name_input.get(),
            "similarity_threshold": float(self.similarity_threshold_input.get()),
            "trigger_when": self.greater_less_var.get(),
            "action_type": self.action_type_var.get(),
        }
        if self.action_type_var.get() == "Email":
            payload["email_to"] = self.email_to_input.get()
            payload["email_body"] = self.email_body_input.get("1.0", tk.END).strip()
        return payload

    def on_action_type_change(self, event=None):
      value = self.action_type_var.get()
      if value == "Email":
          self.show_email_fields()
      else:
          self.hide_email_fields()

    def show_email_fields(self):
        self.email_to_label.grid()
        self.email_to_input.grid()
        self.email_body_label.grid()
        self.email_body_input.grid()

    def hide_email_fields(self):
        self.email_to_label.grid_remove()
        self.email_to_input.grid_remove()
        self.email_body_label.grid_remove()
        self.email_body_input.grid_remove()