from ursina import *
from ursina.camera import Camera
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader, unlit_shader
import ursina.color as ucolor
import random

app = Ursina()

# ===== ワールド =====
ground = Entity(
    model='plane',
    scale=100,
    color=color.gray,
    collider='box'
)

box = Entity(
    model='cube',
    color=color.red,
    position=(0, 1, 0),
    scale=3
)

# ===== プレイヤー =====
player = Entity(position=(0, 2, 0))

# ===== ミニマップカメラ =====
minimap_cam = Camera(parent=player)
minimap_cam.y = 30
minimap_cam.rotation_x = 90
minimap_cam.render_to_texture = True
minimap_cam.ignore = [camera.ui]

# ===== UI表示 =====
minimap_ui = Entity(
    parent=camera.ui,
    model='quad',
    texture=minimap_cam.texture,
    position=(-0.7, 0.4),
    scale=0.3
)

EditorCamera()
app.run()
