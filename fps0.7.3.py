from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina.shaders import unlit_shader
from ursina import *
import ursina.color as ucolor
import random

ZOMBIE_BODY = ucolor.rgb32(80, 95, 70)    # くすんだ緑
ZOMBIE_HEAD = ucolor.rgb32(95, 110, 85)  # 少し明るい
ZOMBIE_ARM = ucolor.rgb32(75, 90, 65)
ZOMBIE_LEG = ucolor.rgb32(45, 45, 45)

MAX_ENEMIES = 25
ENEMY_ATTACK_RANGE = 1.6
ENEMY_ATTACK_DAMAGE = 10
ENEMY_ATTACK_COOLDOWN = 1.2
ENEMY_TURN_SPEED = 6


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

player.hp = 100
player.hp_text = Text(text='HP: 100', position=(-.85, .45), scale=1.5)

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

blood_pools = []

footstep_timer = 0
FOOTSTEP_INTERVAL = 0.35

class Enemy(Entity):

  def __init__(self, **kwargs):
    super().__init__(
        parent=shootables_parent,
        model='models/zombie',
        scale=0.6,
        collider=None,
        **kwargs
    )

    self.rotation_y = 180
    self.shader = lit_with_shadows_shader

    self.walk_time = random.uniform(0, 10)
    self.hp = 100
    self.speed = random.uniform(1.3, 2.0)

    self.attack_timer = 0
    self.dead = False

    # ヒットボックス
    self.collider = BoxCollider(
        self,
        center=Vec3(0, 1.2, 0),
        size=Vec3(1.4, 6.0, 1.4)
    )

    # HPバー
    self.health_bar = Entity(
        parent=self,
        model='cube',
        color=color.red,
        scale=(1.5, .08, .08),
        y=4.3,
        billboard=True
    )

  def damage(self, amount):
    if self.dead:
      return

    self.hp -= amount
    self.health_bar.scale_x = max(self.hp / 100 * 1.5, 0)

    if self.hp <= 0:
      self.dead = True

      # 血だまり増量
      for _ in range(5):
        spawn_blood_decal_from_enemy(self)

      # 血しぶき
      for _ in range(5):
        spawn_blood_effect(
            self.world_position + Vec3(0, 1.2, 0),
            Vec3(0, 1, 0)
        )

      if self in enemies:
        enemies.remove(self)

      destroy(self)

      if len(enemies) < MAX_ENEMIES:
        spawn_enemy(1)

  def update(self):
    if self.dead:
      return

    to_player = player.position - self.position
    dist = Vec2(to_player.x, to_player.z).length()

    if dist > 60:
      return

    # =====================
    # 向く（滑らか）
    # =====================
    target_y = math.degrees(math.atan2(to_player.x, to_player.z))
    self.rotation_y = lerp(
        self.rotation_y,
        target_y,
        time.dt * ENEMY_TURN_SPEED
    )

    # =====================
    # 移動
    # =====================
    if dist > ENEMY_ATTACK_RANGE:
      self.position += self.forward * self.speed * time.dt

      self.walk_time += time.dt * 3
      self.rotation_z = sin(self.walk_time) * 2
      self.y = sin(self.walk_time * 2) * 0.05
      self.rotation_x = 8
    else:
      self.rotation_z = 0
      self.rotation_x = 0

      # =====================
      # 攻撃
      # =====================
    self.attack_timer -= time.dt
    if dist <= ENEMY_ATTACK_RANGE and self.attack_timer <= 0:
      self.attack_timer = ENEMY_ATTACK_COOLDOWN
      self.attack_player()

  def attack_player(self):
    player.hp -= ENEMY_ATTACK_DAMAGE
    player.hp_text.text = f'HP: {player.hp}'


def is_player_moving():
  return held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']

def update():
  global footstep_timer

  # =====================
  # 射撃（← これが無いと弾出ない）
  # =====================
  if held_keys['left mouse']:
    shoot()

  # リコイル
  gun.recoil = lerp(gun.recoil, 0, time.dt * RECOIL_RETURN)
  gun.rotation_x = -gun.recoil

  # =====================
  # 足跡処理
  # =====================
  footstep_timer -= time.dt
  if footstep_timer > 0:
    return

  if not is_player_moving():
    return

  for blood in blood_pools:
    if not blood.enabled:
      continue

    if distance_xz(player.position, blood.position) < 0.6:
      spawn_footprint(
          player.position,
          player.rotation_y + random.uniform(-10, 10)
      )
      footstep_timer = FOOTSTEP_INTERVAL
      break


def spawn_blood_effect(position, direction):
  for i in range(30):  # ← 数を増やすほど激しくなる
    p = Entity(
        model='sphere',
        color=color.rgb(120, 0, 0),
        scale=0.08,
        position=position + direction * 0.2,
        shader=unlit_shader
    )

    # 飛び散りベクトル
    vel = (
        direction * random.uniform(2.5, 4.5) +
        Vec3(
            random.uniform(-1.2, 1.2),
            random.uniform(0.5, 1.8),
            random.uniform(-1.2, 1.2)
        )
    )

    p.velocity = vel
    p.gravity = 9

    def update_particle(p=p):
      p.velocity.y -= p.gravity * time.dt
      p.position += p.velocity * time.dt
      p.scale *= 0.94

      if p.scale.x < 0.01:
        destroy(p)

    p.update = update_particle

# =====================
# 敵生成関数
# =====================
def spawn_enemy(count=1):
  for _ in range(count):
    if len(enemies) >= MAX_ENEMIES:
      return

    e = Enemy(
        position=(
            random.uniform(-25, 25),
            0,
            random.uniform(20, 40)
        )
    )
    enemies.append(e)

# 初期スポーン
spawn_enemy(5)

def spawn_footprint(pos, rotation):
  Entity(
      model='circle',
      color=color.rgb(70, 0, 0),
      position=pos + Vec3(0, 0.011, 0),
      rotation=(90, rotation, 0),
      scale=(0.18, 0.28),            # 足跡サイズ
      shader=unlit_shader
  )

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
      ignore=(player, gun,)
  )

  if hit.entity and isinstance(hit.entity, Enemy):

    spawn_blood_decal_from_enemy(hit.entity)

    spawn_blood_effect(
        hit.world_point,
        hit.world_normal * -1
    )

    hit.entity.damage(25)


# =====================
# 地面の血だまり
# =====================
def spawn_blood_decal_from_enemy(enemy):
  hit = raycast(
      enemy.world_position + Vec3(0, 0.5, 0),
      Vec3(0, -1, 0),
      distance=5,
      ignore=(enemy, player)
  )
  if not hit.hit:
    return

  decal = Entity(
      model='circle',
      color=color.rgb(90, 0, 0),
      position=hit.world_point + Vec3(0, 0.01, 0),
      rotation=(90, random.uniform(0, 360), 0),
      scale=random.uniform(0.5, 0.9),
      shader=unlit_shader
  )

  blood_pools.append(decal)


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
