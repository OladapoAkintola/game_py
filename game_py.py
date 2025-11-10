# tkengine2.py
import tkinter as tk
import time
import pygame.mixer as mixer
from tkinter import PhotoImage

# -------------------------
# Audio System
# -------------------------
class Sound:
    def __init__(self, path):
        self.sound = mixer.Sound(path)
    def play(self, loops=0):
        self.sound.play(loops=loops)
    def stop(self):
        self.sound.stop()
    def set_volume(self, vol):
        self.sound.set_volume(vol)

class Music:
    def __init__(self, path):
        self.path = path
    def play(self, loops=-1):
        mixer.music.load(self.path)
        mixer.music.play(loops=loops)
    def stop(self):
        mixer.music.stop()
    def set_volume(self, vol):
        mixer.music.set_volume(vol)

# Initialize mixer
mixer.init()

# -------------------------
# Timer
# -------------------------
class Timer:
    def __init__(self, window, delay_ms, callback, repeat=False):
        self.window = window
        self.delay = delay_ms
        self.callback = callback
        self.repeat = repeat
        self._start()

    def _start(self):
        self.window.root.after(self.delay, self._run)

    def _run(self):
        self.callback()
        if self.repeat:
            self._start()

# -------------------------
# Sprite Classes
# -------------------------
class Sprite:
    def __init__(self, canvas, x=0, y=0, width=50, height=50, color="red", image=None, layer=0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.layer = layer
        self.image = image
        if image:
            self.id = self.canvas.create_image(x, y, image=image, anchor="nw", tags=("sprite",))
        else:
            self.id = self.canvas.create_rectangle(x, y, x+width, y+height, fill=color, tags=("sprite",))
        self.active = True

    def move(self, dx, dy):
        self.canvas.move(self.id, dx, dy)
        self.x += dx
        self.y += dy

    def set_position(self, x, y):
        self.move(x - self.x, y - self.y)

    def get_position(self):
        return self.x, self.y

    def collide_with(self, other):
        x1, y1, x2, y2 = self.canvas.bbox(self.id)
        ox1, oy1, ox2, oy2 = self.canvas.bbox(other.id)
        return not (x2 < ox1 or x1 > ox2 or y2 < oy1 or y1 > oy2)

class AnimationSprite(Sprite):
    def __init__(self, canvas, frames, x=0, y=0, speed=0.1, layer=0):
        super().__init__(canvas, x=x, y=y, width=frames[0].width(), height=frames[0].height(), image=frames[0], layer=layer)
        self.frames = frames
        self.frame_index = 0
        self.speed = speed
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.canvas.itemconfig(self.id, image=self.frames[self.frame_index])

# -------------------------
# Window Class
# -------------------------
class Window:
    def __init__(self, width=800, height=600, title="TkEngine2 Game", bg="black", fps=60):
        self.root = tk.Tk()
        self.root.title(title)
        self.width = width
        self.height = height
        self.bg = bg
        self.fps = fps
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg=bg)
        self.canvas.pack()
        self.sprites = []
        self.widgets = []
        self.update_callback = None
        self.draw_callback = None
        self.held_keys = set()
        self.mouse_pos = (0,0)
        self.mouse_pressed = False

        # Input bindings
        self.root.bind("<KeyPress>", self._key_press)
        self.root.bind("<KeyRelease>", self._key_release)
        self.root.bind("<Button-1>", self._mouse_click)
        self.root.bind("<Motion>", self._mouse_move)

    # -------------------------
    # Add Sprites / Widgets
    # -------------------------
    def add_sprite(self, sprite):
        self.sprites.append(sprite)
        return sprite

    def add_widget(self, widget, x=0, y=0):
        self.widgets.append(widget)
        widget.place(x=x, y=y)
        return widget

    # -------------------------
    # Input handlers
    # -------------------------
    def _key_press(self, event):
        self.held_keys.add(event.keysym)
    def _key_release(self, event):
        if event.keysym in self.held_keys:
            self.held_keys.remove(event.keysym)
    def _mouse_click(self, event):
        self.mouse_pressed = True
        self.mouse_pos = (event.x, event.y)
    def _mouse_move(self, event):
        self.mouse_pos = (event.x, event.y)

    # -------------------------
    # Update / Draw callbacks
    # -------------------------
    def on_update(self, func):
        self.update_callback = func
    def on_draw(self, func):
        self.draw_callback = func

    # -------------------------
    # Main game loop
    # -------------------------
    def run(self):
        last_time = time.time()
        def loop():
            nonlocal last_time
            now = time.time()
            dt = now - last_time
            last_time = now
            if self.update_callback:
                self.update_callback(dt)
            if self.draw_callback:
                self.draw_callback()
            self.mouse_pressed = False
            self.root.after(int(1000/self.fps), loop)
        loop()
        self.root.mainloop()