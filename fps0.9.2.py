import math
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader, unlit_shader
import ursina.color as ucolor
import random

app = Ursina()   # ← これが最初！！
Text.default_font = 'Xirod.otf'
Entity.default_shader = lit_with_shadows_shader
ENEMY_DETECT_RADIUS = 18   # ← 追跡開始距離（m）

# =====================
# 鍵システム
# =====================
KEY_FRAGMENTS_NEEDED = 3
key_fragments = 0
has_key = False
key_text = Text(
    text=f'Key: 0/{KEY_FRAGMENTS_NEEDED}',
    position=(-0.75, -0.42),
    scale=1.3,
    color=color.yellow
)
# =====================
class KeyFragment(Entity):
  def __init__(self, position):
    super().__init__(
        model='cube',
        color=color.yellow,
        scale=0.25,
        position=position + Vec3(0, 0.3, 0),
        collider='box',
        shader=unlit_shader
    )
    self.rotation_y = random.uniform(0, 360)

  def update(self):
    self.rotation_y += time.dt * 90

    if distance(self.position, player.position) < 1:
      collect_key_fragment(self)

def collect_key_fragment(fragment):
  global key_fragments, has_key

  key_fragments += 1
  key_text.text = f'Key: {key_fragments}/{KEY_FRAGMENTS_NEEDED}'
  destroy(fragment)

  if key_fragments >= KEY_FRAGMENTS_NEEDED:
    has_key = True
    key_text.text = 'Key: COMPLETE'
    key_text.color = color.lime


ZOMBIE_BODY = ucolor.rgb32(80, 95, 70)    # くすんだ緑
ZOMBIE_HEAD = ucolor.rgb32(95, 110, 85)  # 少し明るい
ZOMBIE_ARM = ucolor.rgb32(75, 90, 65)
ZOMBIE_LEG = ucolor.rgb32(45, 45, 45)

MAX_ENEMIES = 25
ENEMY_ATTACK_RANGE = 1.6
ENEMY_ATTACK_DAMAGE = 10
ENEMY_ATTACK_COOLDOWN = 1.2
ENEMY_TURN_SPEED = 4

# =====================
# 効果音
# =====================
# =====================
# 効果音（必ず spatial=False）
# =====================
gun_sound = Audio('gun', autoplay=False, spatial=False)
hit_sound = Audio('hit', autoplay=False, spatial=False)
death_sound = Audio('death', autoplay=False, spatial=False)
footstep_sound = Audio('footstep', autoplay=False, spatial=False)

# =====================
# マップ（表示用）
# =====================
map_entity = Entity(
    model='models/map',
    scale=1,
    collider=None
)

map_entity.collider = BoxCollider(
    map_entity,
    center=Vec3(0, 7.8 + 5.5, 0),      # 元の中心 + 床の高さ
    size=Vec3(90.6, 15.6, 90.5)
)
map_entity.collider.visible = True
map_entity.collider.color = color.rgba(0, 255, 0, 80)

# =====================
# 手動スポーン位置（調整用）
# =====================
ENEMY_SPAWN_POS = Vec3(
    2.0,   # ← x（左右）
    6.0,   # ← y（高さ）
    -6.5   # ← z（前後）
)
# =====================
# 設定メニュー + ぼかし
# =====================
settings_open = False

settings_ui = Entity(
    parent=camera.ui,
    enabled=False
)

# 疑似ぼかし（暗い半透明）
blur_overlay = Entity(
    parent=settings_ui,
    model='quad',
    color=color.rgba(0, 0, 0, 160),
    scale=(2, 2),
    z=1
)

settings_panel = Entity(
    parent=settings_ui,
    model='quad',
    color=color.dark_gray,
    scale=(0.55, 0.45),
    z=0
)

Text(
    parent=settings_panel,
    text='MENU',
    y=0.18,
    scale=2.2,
    origin=(0, 0)
)
def resume_game():
  global settings_open
  settings_open = False
  settings_ui.enabled = False
  mouse.locked = True
  application.paused = False

Button(
    parent=settings_panel,
    text='Resume',
    scale=(0.45, 0.09),
    y=0.10,
    color=color.azure,
    on_click=resume_game
)
def toggle_fullscreen():
  window.fullscreen = not window.fullscreen
Button(
    parent=settings_panel,
    text='Fullscreen ON/OFF',
    scale=(0.45, 0.09),
    y=0.00,
    on_click=toggle_fullscreen
)

MOUSE_SENSITIVITY = 40  # 初期値

def change_sensitivity(value):
  player.mouse_sensitivity = Vec2(value, value)

Text(
    parent=settings_panel,
    text='Sensitivity',
    scale=2.0,
    y=-0.12,
    z=-0.01,
    origin=(0, 0)
)
def apply_sensitivity():
  try:
    value = float(sensitivity_input.text)
    value = clamp(value, 10, 100)  # 安全範囲
    player.mouse_sensitivity = Vec2(value, value)
    sensitivity_input.text = str(int(value))
  except:
    sensitivity_input.text = '40'

sensitivity_input = InputField(
    parent=settings_panel,
    default_value='40',
    y=-0.20,
    scale=(0.25, 0.06),
    character_limit=3,
    z=-0.02
)

sensitivity_input.on_submit = apply_sensitivity
sensitivity_input.color = color.light_gray
sensitivity_input.text_color = color.black

# ======================================
# 4. Quit game
# ======================================
Button(
    parent=settings_panel,
    text='Quit',
    scale=(0.45, 0.09),
    y=-0.32,
    color=color.red,
    on_click=application.quit
)

gun_sound_playing = False

gun_sound.volume = 0.8
hit_sound.volume = 0.9
death_sound.volume = 1.0
footstep_sound.volume = 0.4

is_firing = False

random.seed(0)
Entity.default_shader = lit_with_shadows_shader

# =====================
# プレイヤー
# =====================
player = FirstPersonController(
    origin_y=-.5,
    speed=8,
    collider='box'
)
player.position = (0, 5.5, 0)
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))
player.is_dead = False
# =====================
# 被弾エフェクト
# =====================
player.hit_flash = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(255, 0, 0, 50),
    scale=(2, 2),
    enabled=False
)
player.mouse_sensitivity = Vec2(40, 40)

dead_ui = Entity(parent=camera.ui, enabled=False)

dead_image = Entity(
    parent=dead_ui,
    model='quad',
    texture='wasted.png',
    scale=(1.0, 1.0),
    color=color.white,
    z=-1,
    enabled=True
)

dead_image.alpha = 0   # ← ★ 必ず Entity 作成後に書く

sun = DirectionalLight(shadows=True)
sun.look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(60, 60, 60, 255))
# ADSとHIPの銃位置・FOV
ADS_POS = Vec3(0.005, -0.265, 0.4)     # 照準時の銃位置（要調整）
HIP_POS = Vec3(0.4, -0.35, 0.7)   # 通常時の銃位置

ADS_FOV = 80     # ズーム
HIP_FOV = 90     # 通常
is_ads = False
ADS_RECOIL_MULT = 0.4   # ADS中は40%
HIP_RECOIL_MULT = 1.0  # 通常

# =====================
# 銃
# =====================
gun = Entity(
    parent=camera,
    model='gun',        # ← gun.glb
    position=(0.4, -0.35, 0.6),
    rotation=(0, 0, 0),
    scale=0.004
)

gun.muzzle_flash = Entity(
    parent=gun,
    model='quad',
    position=(0, 0, 1.55),
    scale=0.25,
    color=color.yellow,
    enabled=False
)
MINIMAP_RADIUS = 0.15
MINIMAP_SCALE = 0.01

minimap = Entity(
    parent=camera.ui,
    model='circle',          # ★ quad → circle
    color=color.black,
    scale=(MINIMAP_RADIUS * 2, MINIMAP_RADIUS * 2),
    position=(-0.75, 0.4),
    z=-1
)

player_dot = Entity(
    parent=minimap,
    model='quad',
    texture='player_arrow',
    color=color.white,
    scale=(0.04, 0.08),
    z=-0.01          # ★ 必須
)

# =====================
# ミニマップ：出口ドット
# =====================
exit_dot = Entity(
    parent=minimap,   # ← 正解
    model='circle',
    color=color.lime,
    scale=0.03,
    z=-0.01,
    enabled=True
)
enemy_dots = []

def register_enemy(enemy):
  dot = Entity(
      parent=minimap,
      model='circle',
      color=color.red,
      scale=0.018,
      z=-0.01       # ★ 必須
  )
  enemy_dots.append((enemy, dot))


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

gun_sound = Audio(
    'gun',
    autoplay=False,
    spatial=False,
    loop=True      # ← これ重要
)

ammo_text = Text(
    text=f'Ammo: {ammo}/{MAX_AMMO}',
    position=(0.45, -0.45),
    scale=1.5
)

reload_text = Text(
    text='Reload',
    origin=(0, 0),
    position=(0, 0),
    scale=3,
    color=color.red,
    enabled=False
)
minimap_frame = Entity(
    parent=camera.ui,
    model='circle',
    color=color.white,
    scale=(MINIMAP_RADIUS * 2.1, MINIMAP_RADIUS * 2.1),
    position=minimap.position,
    z=-0.9
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
    self.base_y = self.y
    self.ground_y = self.y
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
      # 鍵の破片ドロップ（30%）
      if random.random() < 0.3:
        KeyFragment(self.world_position)

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
    if self.dead or player.is_dead:
      return

    # プレイヤーとの水平距離
    to_player = player.position - self.position
    dist = Vec2(to_player.x, to_player.z).length()

    # =====================
    # 範囲外 → 何もしない
    # =====================
    if dist > ENEMY_DETECT_RADIUS:
      self.rotation_z = 0
      self.rotation_x = 0
      self.attack_timer -= time.dt
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
    # 移動 or 攻撃
    # =====================
    if dist > ENEMY_ATTACK_RANGE:
      self.position += self.forward * self.speed * time.dt

      self.walk_time += time.dt * 3
      self.rotation_z = sin(self.walk_time) * 2
      self.y = self.base_y + sin(self.walk_time * 2) * 0.05
      self.rotation_x = 8
    else:
      self.rotation_z = 0
      self.rotation_x = 0

      # 攻撃
      self.attack_timer -= time.dt
      if self.attack_timer <= 0:
        self.attack_timer = ENEMY_ATTACK_COOLDOWN
        self.attack_player()

  def attack_player(self):
    if player.hp <= 0:
      return
    hit_sound.play()

    player.hp -= ENEMY_ATTACK_DAMAGE
    player.hp = max(player.hp, 0)
    player.hp_text.text = f'HP: {player.hp}'

    player.hit_flash.enabled = True
    player.hit_flash.alpha = 0.4

    def fade():
      player.hit_flash.alpha = lerp(
          player.hit_flash.alpha,
          0,
          time.dt * 12
      )
      if player.hit_flash.alpha < 0.01:
        player.hit_flash.disable()
        player.hit_flash.update = None
    player.hit_flash.update = fade

    if player.hp <= 0:
      player_die()

exit_door = Entity(
    model='cube',
    scale=(3, 5, 1),
    position=(42, 8, 8.5),
    collider='box',
    visible=False
)

hint_text = Text(
    text='Need Key',
    origin=(0, 0),
    position=(0, -0.25),
    scale=2,
    color=color.orange,
    enabled=False
)

player.hp = 100
player.max_hp = 100

player.hp_text = Text(
    text='HP: 100',
    position=(-0.75, -0.35),
    scale=1.5,
    color=color.green
)

reload_blink_timer = 0
RELOAD_BLINK_SPEED = 6   # 大きいほど速く点滅

def is_player_moving():
  return (
      held_keys['w'] or
      held_keys['a'] or
      held_keys['s'] or
      held_keys['d']
  ) and player.enabled


def update():
  update_minimap()
  global footstep_timer, reload_blink_timer
  # ADS補間
  target_pos = ADS_POS if is_ads else HIP_POS
  gun.position = lerp(gun.position, target_pos, time.dt * 10)

  target_fov = ADS_FOV if is_ads else HIP_FOV
  camera.fov = lerp(camera.fov, target_fov, time.dt * 10)
  if is_firing:
    shoot()

  # =====================
  # 銃リコイル
  # =====================
  gun.recoil = lerp(gun.recoil, 0, time.dt * RECOIL_RETURN)
  gun.rotation_x = -gun.recoil

  # =====================
  # Reload 点滅
  # =====================
  if ammo <= 0 and not reloading:
    reload_text.enabled = True
    reload_blink_timer += time.dt * RELOAD_BLINK_SPEED
    reload_text.alpha = abs(sin(reload_blink_timer))
  else:
    reload_text.enabled = False
    reload_text.alpha = 1
  # =====================
  # 出口ヒント表示
  # =====================
  if not has_key and distance(player, exit_door) < 3:
    hint_text.enabled = True
  else:
    hint_text.enabled = False
  # =====================
  # クリア判定
  # =====================
  if has_key and distance(player.position, exit_door.position) < 2:
    game_clear()
  # =====================
  # 足音（正しい）
  # =====================
  if is_player_moving():
    footstep_timer -= time.dt
    if footstep_timer <= 0:
      footstep_sound.play()
      footstep_timer = FOOTSTEP_INTERVAL
  else:
    footstep_timer = 0
    footstep_sound.stop()

  # =====================
  # 血だまり → 足跡
  # =====================
  for blood in blood_pools:
    if not blood.enabled:
      continue

    if distance_xz(player.position, blood.position) < 0.6:
      spawn_footprint(
          player.position,
          player.rotation_y + random.uniform(-10, 10)
      )
      break

def play_gun_sound():
  gun_sound.stop()   # 連射時に詰まらないように
  gun_sound.play()

def player_die():
  if player.is_dead:
    return

  player.is_dead = True

  player.disable()
  mouse.locked = False

  dead_ui.enabled = True

  dead_image.alpha = 0
  dead_image.animate(
      'alpha',
      1,
      duration=1.0,
      curve=curve.linear
  )

  death_sound.play()


def respawn_player():
  player.is_dead = False
  # HP回復
  player.hp = player.max_hp
  player.hp_text.text = f'HP: {player.hp}'

  # 位置リセット
  player.position = Vec3(0, 1, 0)
  player.rotation = Vec3(0, 0, 0)

  # 操作復活
  player.enable()
  mouse.locked = True

  # UI非表示
  dead_ui.enabled = False
  player.hit_flash.disable()

def game_clear():
  player.disable()
  mouse.locked = False

  clear_ui = Entity(parent=camera.ui)
  Text(
      parent=clear_ui,
      text='COMPLETE',
      scale=4,
      color=color.lime,
      origin=(0, 0)
  )

def shoot():
  global ammo

  if gun.on_cooldown or reloading or ammo <= 0:
    return

  ammo -= 1
  ammo_text.text = f'Ammo: {ammo}/{MAX_AMMO}'

  gun.on_cooldown = True
  invoke(setattr, gun, 'on_cooldown', False, delay=.15)

  gun.muzzle_flash.enabled = True
  invoke(gun.muzzle_flash.disable, delay=.05)

  recoil_mult = ADS_RECOIL_MULT if is_ads else HIP_RECOIL_MULT
  gun.recoil += RECOIL_KICK * recoil_mult

  hit = raycast(
      camera.world_position,
      camera.forward,
      distance=100,
      ignore=(player, gun)
  )
  if hit.entity and isinstance(hit.entity, Enemy):
    spawn_blood_decal_from_enemy(hit.entity)
    spawn_blood_effect(hit.world_point, hit.world_normal * -1)
    hit.entity.damage(25)

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

def update_minimap():
    # ミニマップは固定
  minimap.rotation_z = 0

  # プレイヤーは常に上
  player_dot.position = (0, 0)
  player_dot.rotation_z = 0

  angle = math.radians(player.rotation_y)

  # =====================
  # 敵（赤点）
  # =====================
  for enemy, dot in enemy_dots[:]:
    if not enemy or not enemy.enabled:
      dot.enabled = False
      continue

    dx = enemy.x - player.x
    dz = enemy.z - player.z

    rx = dx * math.cos(angle) - dz * math.sin(angle)
    rz = dx * math.sin(angle) + dz * math.cos(angle)
    x = rx * MINIMAP_SCALE
    y = rz * MINIMAP_SCALE

    dist = math.sqrt(x * x + y * y)
    if dist > MINIMAP_RADIUS:
      dot.enabled = False
      continue

    dot.enabled = True
    dot.position = (x, y)

  # =====================
  # 出口（範囲内は距離反映 / 外は縁）
  # =====================
  dx = exit_door.x - player.x
  dz = exit_door.z - player.z
  # ワールド距離
  world_dist = math.sqrt(dx * dx + dz * dz)

  # プレイヤー向き基準へ
  rx = dx * math.cos(angle) - dz * math.sin(angle)
  rz = dx * math.sin(angle) + dz * math.cos(angle)

  EXIT_DOT_RADIUS = 0.015
  FRAME_MARGIN = 0.01
  max_r = MINIMAP_RADIUS - EXIT_DOT_RADIUS - FRAME_MARGIN

  # ミニマップ上での距離
  map_dist = world_dist * MINIMAP_SCALE

  if map_dist <= max_r:
    # 🟢 ミニマップ内 → 距離反映
    x = rx * MINIMAP_SCALE
    y = rz * MINIMAP_SCALE
  else:
    # 🔵 ミニマップ外 → 縁に固定
    length = math.sqrt(rx * rx + rz * rz)
    if length != 0:
      rx /= length
      rz /= length
    x = rx * max_r
    y = rz * max_r

  exit_dot.enabled = True
  exit_dot.position = (x, y)


# =====================
# 敵生成関数
# =====================
def spawn_enemy(count=1):
  for _ in range(count):
    if len(enemies) >= MAX_ENEMIES:
      return
    e = Enemy(position=ENEMY_SPAWN_POS)
    enemies.append(e)
    register_enemy(e)


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
  reload_text.enabled = False
  ammo_text.text = 'Reloading...'

  def finish():
    global ammo, reloading
    ammo = MAX_AMMO
    ammo_text.text = f'Ammo: {ammo}/{MAX_AMMO}'
    reloading = False

  invoke(finish, delay=1.5)

def input(key):
  global is_firing, gun_sound_playing, is_ads, settings_open

  # ===== ESC メニュー =====
  if key == 'escape':
    settings_open = not settings_open
    settings_ui.enabled = settings_open

    if settings_open:
      mouse.locked = False
      application.paused = True
    else:
      mouse.locked = True
      application.paused = False

  # ===== 射撃 =====
  if key == 'left mouse down':
    is_firing = True

  if key == 'left mouse up':
    is_firing = False
    gun_sound.stop()
    gun_sound_playing = False

  # ===== ADS =====
  if key == 'right mouse down':
    is_ads = True

  if key == 'right mouse up':
    is_ads = False

  # ===== リロード =====
  if key == 'r':
    reload()

  # ===== リスポーン =====
  if key == 'f' and dead_ui.enabled:
    respawn_player()

app.run()
