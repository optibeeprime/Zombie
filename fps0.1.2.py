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
Sky(color=color.black)   # 外は闇

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
# 洋館パラメータ
# ======================
ROOM = 6
H = 3
map_parent = Entity()

wall_tex = 'brick'
floor_tex = 'grass'

occupied = set()

# ======================
# 基本部屋生成
# ======================
def room(pos):
  x, z = pos
  if pos in occupied:
    return
  occupied.add(pos)

  wx = x * ROOM
  wz = z * ROOM

  # 床
  Entity(parent=map_parent, model='cube',
         texture=floor_tex,
         scale=(ROOM, 0.1, ROOM),
         position=(wx, 0, wz),
         collider='box')

  # 天井
  Entity(parent=map_parent, model='cube',
         color=color.rgb(60, 60, 60),
         scale=(ROOM, 0.1, ROOM),
         position=(wx, H, wz))

  # 壁
  for dx, dz in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
    neighbor = (x + dx, z + dz)
    if neighbor in occupied:
      continue

    wall = Entity(
        parent=map_parent,
        model='cube',
        texture=wall_tex,
        scale=(ROOM if dx == 0 else 0.1,
               H,
               ROOM if dz == 0 else 0.1),
        position=(wx + dx * ROOM / 2,
                  H / 2,
                  wz + dz * ROOM / 2),
        collider='box'
    )

    # 外壁なら窓
    if abs(x) > 2 or abs(z) > 2:
      Entity(
          parent=wall,
          model='cube',
          color=color.black,
          scale=(1.5, 1, 0.05),
          position=(0, 0, 0.51 if dz != 0 else 0)
      )

# ======================
# 洋館生成
# ======================
# 中央ホール（大部屋）
for x in range(-1, 2):
  for z in range(-1, 2):
    room((x, z))

# 廊下をランダム延長
def extend_corridor(start, length):
  x, z = start
  dx, dz = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
  for i in range(length):
    x += dx
    z += dz
    room((x, z))

    # 途中で部屋を枝分かれ
    if random.random() < 0.4:
      sx, sz = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
      room((x + sx, z + sz))

# 4方向に廊下
for _ in range(4):
  extend_corridor((0, 0), random.randint(3, 6))

player.position = (0, 1, 0)

app.run()
