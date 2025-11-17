from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Notebook")

root.geometry("500x500")

my_notebook = ttk.Notebook(root)
my_notebook.pack(pady=15)

f_1 = Frame(my_notebook, width=250, height= 250)
f_2 = Frame(my_notebook, width=250, height= 250, bg="purple" )

f_1_inner = Frame(f_1, width=500, height=500, bg="grey")
f_1_inner.place(relx=0.5, rely=.5, anchor="center")

f_1_label = Label(f_1, 
                  text="Cedar",
                  bg="pink"
                  )
f_1_label.place(relx=0,rely=0, anchor="nw")

Label(f_2, text="MARVA", bg='Purple').place(relx=0,rely=0, anchor="nw")

my_notebook.pack(fill="both",expand=1)

my_notebook.add(f_1,text='Frame 1')
my_notebook.add(f_2, text= "Frame 2")

my_notebook.bind("<<NotebookTabChanged>>",
                 lambda event: root.update_idletasks())

def hide():
  my_notebook.hide(0)

bt_2 = ttk.Button(
  f_2, 
  text='Frame 2 button',
  command= hide,
)

bt_2.place(relx=0,rely=0.5, anchor="w")


root.mainloop()