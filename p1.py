import tkinter as tk
import subprocess

from PIL import ImageTk, Image
def execute_code():
    subprocess.Popen(['python', 'projectdsl.py'])

root = tk.Tk()
root.title("Project")
image_file = tk.PhotoImage(file="f1.png")
image_1 = image_file.subsample(1,1)
background_label = tk.Label(root, image=image_1)
background_label.place(x=0, y=100, relwidth=1, relheight=1)
label1=tk.Label(root,text="HOSPITAL EMERGENCY ROOM SIMULATION", font=("Times New Roman",40))
label1.place(x=275,y=30)
button = tk.Button(root, text="START", command=execute_code,bg="#5fe0ec", fg="white", font=("Arial", 26))
button.place(x=950,y=400)
#root.attributes("-fullscreen", True)
root.mainloop()
