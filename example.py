# ultimate_td_demo.py
from game_py import Window, Sprite, Timer
from tkinter import PhotoImage, Label
import random

# -------------------------
# Guard audio import
# -------------------------
try:
    from game_py import Sound, Music
    mixer_available = True
except:
    mixer_available = False
    print("Audio disabled: pygame.mixer not available")

# -------------------------
# Window Setup
# -------------------------
win = Window(800, 600, "Ultimate Tower Defense", bg="skyblue", fps=60)

# -------------------------
# Player / Game State
# -------------------------
currency = 100
towers = []
enemies = []

# Display currency using a Tkinter label
currency_label = Label(win.root, text=f"Currency: {currency}", font=("Arial", 16), bg="yellow")
win.add_widget(currency_label, x=10, y=10)

# -------------------------
# Tower Class
# -------------------------
class Tower(Sprite):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x=x, y=y, width=40, height=40, color="blue")
        self.range = 120
        self.damage = 10
        self.cooldown = 0.5
        self.last_shot = 0

    def update(self, dt):
        self.last_shot += dt
        for enemy in enemies:
            if self.last_shot >= self.cooldown and self.in_range(enemy):
                enemy.health -= self.damage
                self.last_shot = 0
                if mixer_available:
                    try:
                        hit_sound.play()
                    except:
                        pass

    def in_range(self, enemy):
        ex, ey = enemy.get_position()
        return ((self.x - ex)**2 + (self.y - ey)**2) ** 0.5 <= self.range

# -------------------------
# Enemy Class
# -------------------------
class Enemy(Sprite):
    def __init__(self, canvas, x, y, health=50, speed=50):
        super().__init__(canvas, x=x, y=y, width=30, height=30, color="red")
        self.health = health
        self.speed = speed

    def update(self, dt):
        self.move(self.speed * dt, 0)  # Move right
        if self.x > win.width:
            self.set_position(0, random.randint(50, win.height-50))
            self.health = 50

# -------------------------
# Place Towers on Mouse Click
# -------------------------
def place_tower():
    global currency
    x, y = win.mouse_pos
    if currency >= 50:
        tower = Tower(win.canvas, x-20, y-20)
        towers.append(tower)
        win.add_sprite(tower)
        currency -= 50
        currency_label.config(text=f"Currency: {currency}")

win.root.bind("<Button-1>", lambda e: place_tower())

# -------------------------
# Spawn Enemies Periodically
# -------------------------
def spawn_enemy():
    enemy = Enemy(win.canvas, x=0, y=random.randint(50, win.height-50))
    enemies.append(enemy)
    win.add_sprite(enemy)

# Timer: spawn enemy every 2 seconds
Timer(win, 2000, spawn_enemy, repeat=True)

# -------------------------
# Load Audio (optional)
# -------------------------
if mixer_available:
    try:
        hit_sound = Sound("hit.wav")   # Replace with your sound file
        bg_music = Music("bg_music.mp3")  # Replace with your music file
        bg_music.play(loops=-1)
    except:
        print("Failed to load audio files")

# -------------------------
# Game Update Loop
# -------------------------
def update(dt):
    global currency
    for t in towers:
        t.update(dt)
    for e in enemies[:]:
        e.update(dt)
        if e.health <= 0:
            try:
                win.canvas.delete(e.id)
            except:
                pass
            enemies.remove(e)
            currency += 20
            currency_label.config(text=f"Currency: {currency}")

win.on_update(update)

# -------------------------
# Optional Draw Loop
# -------------------------
def draw():
    pass

win.on_draw(draw)

# -------------------------
# Run Game
# -------------------------
win.run()