import tkinter as tk
from component.utilities import add_image_button, get_photo_image
from definitions import ADD_BUTTON_FILE

app = tk.Tk()
app.wm_geometry("750x500")
f = tk.Frame(master=app)
f.pack(expand=True, fill="both")

add_image_button(f, get_photo_image(ADD_BUTTON_FILE))

app.mainloop()
