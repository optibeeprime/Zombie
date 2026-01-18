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
# 洋館パラメータ
# ======================
ROOM = 6
H = 3
map_parent = Entity()

wall_tex = 'brick'
floor_tex = 'grass'

GRID = 9
rooms = {}

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
# 実体化
# ======================
for (x, z), data in rooms.items():
  wx, wz = x * ROOM, z * ROOM

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

  # 壁（通路が無い方向だけ）
  for k, (dx, dz) in dirs.items():
    if k in data['open']:
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
    if abs(x) == GRID // 2 or abs(z) == GRID // 2:
      Entity(
          parent=wall,
          model='cube',
          color=color.black,
          scale=(1.5, 1, 0.05),
          position=(0, 0, 0.51 if dz != 0 else 0)
      )

player.position = (0, 1, 0)

app.run()
