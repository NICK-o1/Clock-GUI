from PIL import Image, ImageTk
import urllib.request
import io
import random
import tkinter as tk
from datetime import datetime
import configparser

# Load config
config = configparser.ConfigParser()
config.read("config.cfg")

# Load color list
colors = dict(config.items("COLORS"))

# Load font list
fonts = dict(config.items("FONTS"))

def get_color(name):
    return colors.get(name, name)

def get_font(name, size):
    family = fonts.get(name, name)
    return (family, int(size))

def randomize_colors():
    available = [c for c in colors.values() if c.lower() not in ["#000000", "#1e1e1e"]]
    random_color = random.choice(available)
    time_label.config(fg=random_color)
    date_label.config(fg=random_color)

# Read theme settings
bg_color = get_color(config["THEME"].get("background", "black"))
time_color = get_color(config["THEME"].get("time_color", "white"))
date_color = get_color(config["THEME"].get("date_color", "white"))

time_font_name, time_font_size = config["THEME"].get("time_font", "Helvetica 32").split()
date_font_name, date_font_size = config["THEME"].get("date_font", "Helvetica 16").split()

time_font = get_font(time_font_name, time_font_size)
date_font = get_font(date_font_name, date_font_size)

transparency = float(config["THEME"].get("transparency", 1.0))
always_on_top = config["THEME"].getboolean("always_on_top", True)

# ---------------- BACKGROUND LOADER ---------------- #

def load_background():
    mode = config["THEME"].get("background_mode", "image")

    if mode == "color":
        # Solid color background
        color = config["THEME"].get("background_color", "#000000")
        background_label.config(image="", bg=color)
        background_label.image = None
        return

    # Otherwise load image
    try:
        url = config["THEME"].get("background_url", "https://picsum.photos/1920/1080")
        with urllib.request.urlopen(url) as response:
            data = response.read()

        img = Image.open(io.BytesIO(data))
        img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)

        bg_image = ImageTk.PhotoImage(img)
        background_label.config(image=bg_image)
        background_label.image = bg_image

    except Exception as e:
        print("Error loading background:", e)

# ---------------- CLOCK UPDATE ---------------- #

def update_clock():
    now = datetime.now()
    time_string = now.strftime("%I:%M:%S %p")
    date_string = now.strftime("%A, %d %B %Y")

    time_label.config(text=time_string)
    date_label.config(text=date_string)

    randomize_colors()

    # Change background every 10 seconds (only in image mode)
    if config["THEME"].get("background_mode", "image") == "image":
        if int(now.strftime("%S")) % 10 == 0:
            load_background()

    root.after(1000, update_clock)

# ---------------- DRAGGING ---------------- #

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

# ---------------- WINDOW SETUP ---------------- #

root = tk.Tk()

# Background image layer
background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Fullscreen
root.attributes("-fullscreen", True)

# Close button
close_btn = tk.Label(root, text="  X  ", fg="white", bg="red",
                     font=("Arial", 16, "bold"))
close_btn.place(relx=1.0, rely=0.0, anchor="ne")

def close_app(event=None):
    root.destroy()

close_btn.bind("<Button-1>", close_app)

# Window styling
root.overrideredirect(True)
root.attributes("-topmost", always_on_top)
root.attributes("-alpha", transparency)
root.config(bg=bg_color)

# Time + Date labels (transparent background)
time_label = tk.Label(root, font=time_font, fg=time_color, bg="Black")
date_label = tk.Label(root, font=date_font, fg=date_color, bg="Black")

# Center them
time_label.place(relx=0.5, rely=0.45, anchor="center")
date_label.place(relx=0.5, rely=0.55, anchor="center")

# Dragging
for widget in (time_label, date_label):
    widget.bind("<ButtonPress-1>", start_move)
    widget.bind("<ButtonRelease-1>", stop_move)
    widget.bind("<B1-Motion>", do_move)

# Load first background
load_background()

# Start clock
update_clock()
root.mainloop()