from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

window.fps_counter.enabled = True
mouse.locked = True

# --- 照明 ---
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(80, 80, 80, 255))

Sky(color=color.rgb(30, 30, 30))

scene.fog_density = 0.03
scene.fog_color = color.black

# --- プレイヤー ---
player = FirstPersonController(
    speed=4,
    jump_height=0.8,
    gravity=1
)

# --- 床 ---
# 床（cube）
floor = Entity(
    model='cube',
    texture='asphalt',
    scale=(8, 0.1, 40),
    position=(0, 0, 0),
    collider='box'
)

# 天井（cube）
ceiling = Entity(
    model='cube',
    color=color.rgb(50, 50, 50),
    scale=(8, 0.1, 40),
    position=(0, 3, 0)
)


# --- 壁 ---
left_wall = Entity(
    model='cube',
    texture='brick',
    scale=(1, 3, 40),
    position=(-4, 1.5, 0),
    collider='box'
)

right_wall = Entity(
    model='cube',
    texture='brick',
    scale=(1, 3, 40),
    position=(4, 1.5, 0),
    collider='box'
)

back_wall = Entity(
    model='cube',
    texture='brick',
    scale=(8, 3, 1),
    position=(0, 1.5, -20),
    collider='box'
)

app.run()
