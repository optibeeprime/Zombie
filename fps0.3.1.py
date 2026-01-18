from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import random

app = Ursina()
random.seed(0)

# =====================
# レンダリング設定
# =====================
Entity.default_shader = lit_with_shadows_shader

# =====================
# 環境（空・地面）
# =====================
Sky()

ground = Entity(
    model='plane',
    texture='grass',
    texture_scale=(8, 8),
    scale=128,
    collider='box'
)

sun = DirectionalLight(shadows=True)
sun.look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(60, 60, 60, 255))

# =====================
# プレイヤー
# =====================
player = FirstPersonController(
    model='cube',
    origin_y=-.5,
    speed=8,
    collider='box'
)
player.y = 1

player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))

# =====================
# 銃
# =====================
# =====================
# 銃モデル（組み立て式）
# =====================
gun = Entity(
    parent=camera,
    position=(0.4, -0.3, 0.6),
    rotation=(0, 0, 0)
)

# 本体（レシーバー）
Entity(
    parent=gun,
    model='cube',
    scale=(0.3, 0.15, 0.8),
    position=(0, 0, 0),
    color=color.dark_gray
)

# 銃身（バレル）
Entity(
    parent=gun,
    model='cube',
    scale=(0.08, 0.08, 1.2),
    position=(0, 0, 0.9),
    color=color.black
)

# グリップ
Entity(
    parent=gun,
    model='cube',
    scale=(0.12, 0.3, 0.12),
    position=(0, -0.25, -0.15),
    rotation=(0, 0, -10),
    color=color.gray
)

# マガジン
Entity(
    parent=gun,
    model='cube',
    scale=(0.12, 0.35, 0.2),
    position=(0, -0.35, 0.1),
    color=color.rgb(40, 40, 40)
)

# サイト（照準）
Entity(
    parent=gun,
    model='cube',
    scale=(0.05, 0.05, 0.2),
    position=(0, 0.12, 0.3),
    color=color.black
)

# マズルフラッシュ
gun.muzzle_flash = Entity(
    parent=gun,
    model='quad',
    position=(0, 0, 1.55),
    scale=0.25,
    color=color.yellow,
    enabled=False
)

gun.on_cooldown = False

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

# =====================
# 敵
# =====================
class Enemy(Entity):
  def __init__(self, **kwargs):
    super().__init__(
        parent=shootables_parent,
        model='cube',
        scale_y=2,
        origin_y=-.5,
        color=color.light_gray,
        collider='box',
        **kwargs
    )
    self.max_hp = 100
    self.hp = self.max_hp

    self.health_bar = Entity(
        parent=self,
        model='cube',
        color=color.red,
        scale=(1.5, .1, .1),
        y=1.3
    )

  def update(self):
    dist = distance_xz(player.position, self.position)
    if dist > 50:
      return

    self.look_at_2d(player.position, 'y')

    if dist > 2:
      self.position += self.forward * time.dt * 3

    self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5

  def damage(self, amount):
    self.hp -= amount
    self.blink(color.red)
    if self.hp <= 0:
      destroy(self)

# 敵を平原に配置
enemies = []
for i in range(10):
  enemies.append(
      Enemy(
          x=random.uniform(-30, 30),
          z=random.uniform(-30, 30)
      )
  )

# =====================
# 射撃処理
# =====================
def shoot():
  if gun.on_cooldown:
    return

  gun.on_cooldown = True
  gun.muzzle_flash.enabled = True
  invoke(gun.muzzle_flash.disable, delay=.05)
  invoke(setattr, gun, 'on_cooldown', False, delay=.15)

  hit = raycast(
      camera.world_position,
      camera.forward,
      distance=100,
      ignore=(player,)
  )

  if hit.entity and isinstance(hit.entity, Enemy):
    hit.entity.damage(25)

def update():
  if held_keys['left mouse']:
    shoot()

# =====================
# エディタカメラ切替
# =====================
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

def input(key):
  if key == 'tab':
    editor_camera.enabled = not editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    application.paused = editor_camera.enabled
    editor_camera.position = player.position

app.run()
