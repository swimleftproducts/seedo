from tkinter import ttk

def setup_combo_box_styles():
    style = ttk.Style()
    style.theme_use("clam")  # allows background customization

    # COMBOBOX STYLE
    style.configure(
        "LightBlue.TCombobox",
        fieldbackground="lightblue",     # entry box background
        background="lightblue",          # dropdown button background
        foreground="black"
        
    )
    # Style the dropdown list
    style.configure(
      "LightBlue.TCombobox.Listbox",
      background="lightblue",
      foreground="black",
      selectbackground="darkblue",
      selectforeground="white"
    )

    style.map(
        "LightBlue.TCombobox",
        fieldbackground=[("readonly", "lightblue")],
        foreground=[("readonly", "black")],
        background=[("readonly", "lightblue")]
    )
