from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import random

app = Ursina()
random.seed(0)
Entity.default_shader = lit_with_shadows_shader

# =====================
# 環境
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
    origin_y=-.5,
    speed=8,
    collider='box'
)
player.y = 1
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))

# =====================
# 銃
# =====================
gun = Entity(parent=camera, position=(0.4, -0.3, 0.6))

Entity(parent=gun, model='cube', scale=(0.3, 0.15, 0.8), color=color.dark_gray)
Entity(parent=gun, model='cube', scale=(0.08, 0.08, 1.2),
       position=(0, 0, 0.9), color=color.black)
Entity(parent=gun, model='cube', scale=(0.12, 0.3, 0.12),
       position=(0, -0.25, -0.15), rotation=(0, 0, -10), color=color.gray)
Entity(parent=gun, model='cube', scale=(0.12, 0.35, 0.2),
       position=(0, -0.35, 0.1), color=color.rgb(40, 40, 40))
Entity(parent=gun, model='cube', scale=(0.05, 0.05, 0.2),
       position=(0, 0.12, 0.3), color=color.black)

gun.muzzle_flash = Entity(
    parent=gun,
    model='quad',
    position=(0, 0, 1.55),
    scale=0.25,
    color=color.yellow,
    enabled=False
)

gun.on_cooldown = False
gun.recoil = 0

RECOIL_KICK = 4
RECOIL_RETURN = 18

# =====================
# 弾
# =====================
MAX_AMMO = 30
ammo = MAX_AMMO
reloading = False

ammo_text = Text(
    text=f'Ammo: {ammo}/{MAX_AMMO}',
    position=(.7, -.45),
    scale=1.5
)

# =====================
# 敵
# =====================
shootables_parent = Entity()
mouse.traverse_target = shootables_parent

enemies = []

class Enemy(Entity):
  def __init__(self, **kwargs):
    super().__init__(
        parent=shootables_parent,
        model='zombie',
        scale=1,
        origin_y=-.5,
        collider=None,
        **kwargs
    )

    self.rotation_x = 90
    self.rotation_y = 180
    self.y = 0.5

    self.collider = BoxCollider(
        self,
        center=Vec3(0, 1.1, 0),
        size=Vec3(1.2, 2.3, 1.2)
    )

    self.hp = 100

    self.health_bar = Entity(
        parent=self,
        model='cube',
        color=color.red,
        scale=(1.5, .1, .1),
        y=2.2
    )

  def update(self):
    dist = distance_xz(player.position, self.position)
    if dist > 60:
      return

    self.look_at_2d(player.position, 'y')

    if dist > 2:
      direction = Vec3(self.forward.x, 0, self.forward.z)
      self.position += direction.normalized() * time.dt * 3

    self.y = 0.5
    self.health_bar.world_scale_x = (self.hp / 100) * 1.5

  def damage(self, amount):
    self.hp -= amount
    self.blink(color.red)

    if self.hp <= 0:
      enemies.remove(self)
      destroy(self)

      # 倒したら1体湧く
      spawn_enemy(1)

# =====================
# 敵生成関数
# =====================
def spawn_enemy(count=1):
  for _ in range(count):
    e = Enemy(
        position=(
            random.uniform(-20, 20),
            0,
            random.uniform(15, 35)
        )
    )
    enemies.append(e)

# 初期スポーン
spawn_enemy(5)

# =====================
# 射撃
# =====================
def shoot():
  global ammo

  if gun.on_cooldown or reloading or ammo <= 0:
    return

  ammo -= 1
  ammo_text.text = f'Ammo: {ammo}/{MAX_AMMO}'

  gun.on_cooldown = True
  gun.muzzle_flash.enabled = True
  invoke(gun.muzzle_flash.disable, delay=.05)
  invoke(setattr, gun, 'on_cooldown', False, delay=.15)

  gun.recoil += RECOIL_KICK

  hit = raycast(
      camera.world_position,
      camera.forward,
      distance=100,
      ignore=(player,)
  )

  if hit.entity and isinstance(hit.entity, Enemy):
    hit.entity.damage(25)

# =====================
# リロード
# =====================
def reload():
  global ammo, reloading
  if ammo == MAX_AMMO or reloading:
    return

  reloading = True
  ammo_text.text = 'Reloading...'

  def finish():
    global ammo, reloading
    ammo = MAX_AMMO
    ammo_text.text = f'Ammo: {ammo}/{MAX_AMMO}'
    reloading = False

  invoke(finish, delay=1.5)

# =====================
# 更新
# =====================
def update():
  if held_keys['left mouse']:
    shoot()

  gun.recoil = lerp(gun.recoil, 0, time.dt * RECOIL_RETURN)
  gun.rotation_x = -gun.recoil

# =====================
# 入力
# =====================
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

def input(key):
  if key == 'r':
    reload()

  if key == 'tab':
    editor_camera.enabled = not editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    application.paused = editor_camera.enabled
    editor_camera.position = player.position

app.run()
