import tkinter as tk

window = tk.Tk()
window.title("my window")
window.geometry('400x400')

b1 = tk.Button(window, text="run", width=15, height=2, command=insert_point)

window.mainloop()