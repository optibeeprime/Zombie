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
sun = DirectionalLight(shadows=True)
sun.look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(50, 50, 50, 255))
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
# 階段部屋を選ぶ（中央寄り）
# ======================
stair_room = min(rooms.keys(), key=lambda p: abs(p[0]) + abs(p[1]))

# ======================
# 建築
# ======================
for floor in range(FLOORS):
  y_base = floor * FLOOR_HEIGHT

  for (x, z), data in rooms.items():
    wx, wz = x * ROOM, z * ROOM

    # --- 床 ---
    Entity(
        parent=map_parent,
        model='cube',
        texture=floor_tex,
        scale=(ROOM, 0.1, ROOM),
        position=(wx, y_base, wz),
        collider='box'
    )

    # --- 天井 ---
    Entity(
        parent=map_parent,
        model='cube',
        color=color.rgb(60, 60, 60),
        scale=(ROOM, 0.1, ROOM),
        position=(wx, y_base + FLOOR_HEIGHT, wz)
    )

    # --- 壁 ---
    for k, (dx, dz) in dirs.items():
      if k in data['open']:
        continue

      # 階段部屋は1階の天井を開ける
      if floor == 0 and (x, z) == stair_room:
        continue

      wall = Entity(
          parent=map_parent,
          model='cube',
          texture=wall_tex,
          scale=(ROOM if dx == 0 else 0.1,
                 FLOOR_HEIGHT,
                 ROOM if dz == 0 else 0.1),
          position=(wx + dx * ROOM / 2,
                    y_base + FLOOR_HEIGHT / 2,
                    wz + dz * ROOM / 2),
          collider='box'
      )

      # 外壁のみ窓（1階）
      if floor == 0 and (abs(x) == GRID // 2 or abs(z) == GRID // 2):
        Entity(
            parent=wall,
            model='cube',
            color=color.black,
            scale=(1.5, 1, 0.05),
            position=(0, 0, 0.51 if dz != 0 else 0)
        )

# ======================
# 階段生成（スロープ）
# ======================
sx, sz = stair_room
base_x = sx * ROOM
base_z = sz * ROOM

stairs = Entity(
    parent=map_parent,
    model='cube',
    scale=(2, FLOOR_HEIGHT, ROOM),
    position=(base_x, FLOOR_HEIGHT / 2, base_z),
    rotation=(0, 0, 0),
    collider='box'
)

stairs.rotation_x = -30  # 傾斜

# 2階側の床補助
Entity(
    parent=map_parent,
    model='cube',
    scale=(ROOM, 0.1, ROOM),
    position=(base_x, FLOOR_HEIGHT, base_z),
    collider='box'
)

# ======================
# プレイヤー初期位置
# ======================
player.position = (base_x, 1, base_z - 2)

app.run()
