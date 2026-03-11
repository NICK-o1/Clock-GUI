from PIL import Image, ImageTk
import urllib.request
import io
import random
import tkinter as tk
from datetime import datetime
import configparser
import os

# ---------------- CONFIG LOADING ---------------- #

config = configparser.ConfigParser()
loaded_files = config.read("config.cfg")
print("Loaded config from:", [os.path.abspath(f) for f in loaded_files])

# ---------------- COLOR + FONT HELPERS ---------------- #

colors = dict(config.items("COLORS"))
fonts = dict(config.items("FONTS"))

def get_color(name):
    return colors.get(name, name)

def get_font(name, size):
    family = fonts.get(name, name)
    return (family, int(size))

def randomize_colors():
    available = [c for c in colors.values() if c.lower() not in ["#000000", "#1e1e1e"]]
    if available:
        random_color = random.choice(available)
        time_label.config(fg=random_color)
        date_label.config(fg=random_color)

# ---------------- THEME SETTINGS ---------------- #

bg_color = get_color(config["THEME"].get("background_color", "#000000"))

time_color = get_color(config["THEME"].get("time_color", "white"))
date_color = get_color(config["THEME"].get("date_color", "white"))

time_font_name, time_font_size = config["THEME"].get("time_font", "Helvetica 32").split()
date_font_name, date_font_size = config["THEME"].get("date_font", "Helvetica 16").split()

time_font = get_font(time_font_name, time_font_size)
date_font = get_font(date_font_name, date_font_size)

transparency = float(config["THEME"].get("transparency", 1.0))
always_on_top = config["THEME"].getboolean("always_on_top", True)

# ---------------- ROOT WINDOW ---------------- #

root = tk.Tk()

# Screen size auto-detect
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

# Background label
background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
background_label.lower()

# Fullscreen FIRST
root.attributes("-fullscreen", True)
# Then override redirect
root.overrideredirect(True)
# Then transparency + background
root.attributes("-alpha", transparency)
root.config(bg=bg_color)
# Finally always-on-top
root.attributes("-topmost", always_on_top)

# ---------------- BACKGROUND LOADER ---------------- #

def load_background():
    mode = config["THEME"].get("background_mode", "image")

    if mode == "color":
        color = config["THEME"].get("background_color", "#000000")
        background_label.config(image="", bg=color)
        background_label.image = None
        return

    try:
        url = config["THEME"].get("background_url", "https://picsum.photos/1920/1080")
        with urllib.request.urlopen(url) as response:
            data = response.read()

        img = Image.open(io.BytesIO(data))
        img = img.resize((screen_w, screen_h), Image.LANCZOS)

        bg_image = ImageTk.PhotoImage(img)
        background_label.config(image=bg_image, bg=None)
        background_label.image = bg_image

    except Exception as e:
        print("ERROR loading background:", e)

# ---------------- TOGGLE BACKGROUND MODE ---------------- #

def toggle_background(event=None):
    current = config["THEME"].get("background_mode", "image")
    new_mode = "color" if current == "image" else "image"
    config["THEME"]["background_mode"] = new_mode

    with open("config.cfg", "w") as cfg:
        config.write(cfg)

    print("Switched background mode to:", new_mode)
    load_background()

# ---------------- CLOCK UPDATE ---------------- #

def update_clock():
    now = datetime.now()

    time_label.config(text=now.strftime("%I:%M:%S %p"))
    date_label.config(text=now.strftime("%A, %d %B %Y"))

    randomize_colors()

    if config["THEME"].get("background_mode", "image") == "image":
        if int(now.strftime("%S")) % 10 == 0:
            load_background()

    root.after(1000, update_clock)

# ---------------- BLACK BOX PANELS ---------------- #

time_bg = tk.Label(root, bg="black")
time_bg.place(relx=0.5, rely=0.45, anchor="center")

date_bg = tk.Label(root, bg="black")
date_bg.place(relx=0.5, rely=0.55, anchor="center")

# ---------------- TIME + DATE LABELS ---------------- #

time_label = tk.Label(
    root,
    font=time_font,
    fg=time_color,
    bg="black",
    padx=20,
    pady=10
)

date_label = tk.Label(
    root,
    font=date_font,
    fg=date_color,
    bg="black",
    padx=20,
    pady=10
)

time_label.place(relx=0.5, rely=0.45, anchor="center")
date_label.place(relx=0.5, rely=0.55, anchor="center")

# ---------------- TITLEBAR BUTTON BAR ---------------- #

button_bar = tk.Frame(root, bg="black")
button_bar.place(relx=1.0, rely=0.0, anchor="ne")

# HALF-SCREEN BUTTON (left half)
half_btn = tk.Label(button_bar, text=" ⬛ ", fg="white", bg="gray35",
                    font=("Arial", 16, "bold"))
half_btn.pack(side="left", padx=2)

def half_screen(event=None):
    root.overrideredirect(False)
    root.attributes("-fullscreen", False)

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    new_width = sw // 2
    new_height = sh

    root.geometry(f"{new_width}x{new_height}+0+0")

half_btn.bind("<Button-1>", half_screen)

# MINIMIZE BUTTON
min_btn = tk.Label(button_bar, text=" _ ", fg="white", bg="gray20",
                   font=("Arial", 16, "bold"))
min_btn.pack(side="left", padx=2)

def minimize_app(event=None):
    root.overrideredirect(False)
    root.iconify()

min_btn.bind("<Button-1>", minimize_app)

# CLOSE BUTTON
close_btn = tk.Label(button_bar, text=" X ", fg="white", bg="red",
                     font=("Arial", 16, "bold"))
close_btn.pack(side="left", padx=2)

def close_app(event=None):
    root.destroy()

close_btn.bind("<Button-1>", close_app)

# ---------------- KEYBIND ---------------- #

root.bind("t", toggle_background)

# ---------------- START APP ---------------- #

load_background()
update_clock()
root.mainloop()