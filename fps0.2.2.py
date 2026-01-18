from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import random

app = Ursina()
Entity.default_shader = lit_with_shadows_shader
random.seed()

# ======================
# 環境
# ======================
DirectionalLight(shadows=True).look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(40, 40, 40, 255))
Sky(color=color.black)

# ======================
# プレイヤー
# ======================
player = FirstPersonController(
    origin_y=-.5,
    speed=4,
    collider='box'
)
player.y = 1

# ======================
# パラメータ
# ======================
ROOM = 6
FLOOR_HEIGHT = 3
FLOORS = 2
GRID = 9

wall_tex = 'brick'
floor_tex = 'grass'

map_parent = Entity()

# ======================
# 迷路生成（DFS）
# ======================
dirs = {
    'N': (0, 1),
    'S': (0, -1),
    'E': (1, 0),
    'W': (-1, 0)
}
opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

rooms = {}

def carve(x, z):
  rooms[(x, z)] = {'open': set()}
  d = list(dirs.keys())
  random.shuffle(d)

  for k in d:
    dx, dz = dirs[k]
    nx, nz = x + dx, z + dz
    if abs(nx) > GRID // 2 or abs(nz) > GRID // 2:
      continue
    if (nx, nz) in rooms:
      continue

    rooms[(x, z)]['open'].add(k)
    carve(nx, nz)
    rooms[(nx, nz)]['open'].add(opposite[k])

carve(0, 0)

# ======================
# 階段部屋（中央）
# ======================
stair_room = min(rooms.keys(), key=lambda p: abs(p[0]) + abs(p[1]))
sx, sz = stair_room

# ======================
# 建築
# ======================
for floor in range(FLOORS):
  y = floor * FLOOR_HEIGHT

  for (x, z), data in rooms.items():
    wx, wz = x * ROOM, z * ROOM

    # --- 床（厚みあり）---
    Entity(
        parent=map_parent,
        model='cube',
        texture=floor_tex,
        scale=(ROOM, 0.2, ROOM),
        position=(wx, y, wz),
        collider='box'
    )

    # --- 天井（少し上・物理なし）---
    if not (floor == 0 and (x, z) == stair_room):
      Entity(
          parent=map_parent,
          model='cube',
          color=color.rgb(50, 50, 50),
          scale=(ROOM, 0.1, ROOM),
          position=(wx, y + FLOOR_HEIGHT + 0.05, wz)
      )

    # --- 壁 ---
    for k, (dx, dz) in dirs.items():
      if k in data['open']:
        continue

      Entity(
          parent=map_parent,
          model='cube',
          texture=wall_tex,
          scale=(ROOM if dx == 0 else 0.2,
                 FLOOR_HEIGHT,
                 ROOM if dz == 0 else 0.2),
          position=(wx + dx * ROOM / 2,
                    y + FLOOR_HEIGHT / 2,
                    wz + dz * ROOM / 2),
          collider='box'
      )

# ======================
# 階段（スロープ）
# ======================
base_x = sx * ROOM
base_z = sz * ROOM

stairs = Entity(
    parent=map_parent,
    model='cube',
    scale=(2, FLOOR_HEIGHT, ROOM),
    position=(base_x, FLOOR_HEIGHT / 2, base_z),
    rotation_x=-30,
    collider='box'
)

# 踊り場（2階）
Entity(
    parent=map_parent,
    model='cube',
    scale=(ROOM, 0.2, ROOM),
    position=(base_x, FLOOR_HEIGHT, base_z),
    collider='box'
)

# ======================
# プレイヤー初期位置
# ======================
player.position = (base_x, 1, base_z - 2)

app.run()
