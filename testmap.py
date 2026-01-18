from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from pathlib import Path

app = Ursina()
application.asset_folder = Path('assets')

# プレイヤー
player = FirstPersonController(speed=6)
player.position = (0, 5, 0)
player.collider = 'box'      # ← 超重要
player.gravity = 1

# ライト
DirectionalLight(shadows=True).look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(140, 140, 140, 255))
Sky()

# マップ（背景扱い）
map_entity = Entity(
    model='models/map',
    scale=1,
    collider=None
)

# 見えない床（当たり判定専用）
floor = Entity(
    model='cube',
    scale=(200, 1, 200),
    position=(0, 5, 0),   # ← 上面が y=0
    collider='box',
    visible=False
)

window.fps_counter.enabled = True
window.title = 'Map Collider Test'

app.run()
