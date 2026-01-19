import math
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader, unlit_shader
import ursina.color as ucolor
import random

app = Ursina()
window.size = (1920, 1080)
window.fullscreen = True
window.vsync = True
application.target_fps = 60
Text.default_font = 'assets/Xirod.otf'
Entity.default_shader = lit_with_shadows_shader
ENEMY_DETECT_RADIUS = 18   # ← 追跡開始距離

# =====================
# 鍵
# =====================
KEY_FRAGMENTS_NEEDED = 5
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
  global key_fragments

  key_fragments += 1

  if key_fragments < KEY_FRAGMENTS_NEEDED:
    key_text.text = f'Key: {key_fragments}/{KEY_FRAGMENTS_NEEDED}'
    key_text.color = color.yellow
  else:
    # ★ 5/5 到達時
    key_text.text = 'Key: READY'
    key_text.color = color.orange

  destroy(fragment)


enemy_key_drops = 0
MAX_ENEMY_KEY_DROPS = 3
KeyFragment(Vec3(-13.6, 10.5, -14))
KeyFragment(Vec3(-28.5, 11, -26))

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
gun_sound = Audio('gun', autoplay=False, spatial=False)
# hit_sound = Audio('hit', autoplay=False, spatial=False)
death_sound = Audio('death', autoplay=False, spatial=False)
footstep_sound = Audio('footstep', autoplay=False, spatial=False)

enemy_walls = []

# =====================
# マップ
# =====================
map_entity = Entity(
    model='models/map',
    scale=1,
    collider=None
)

map_entity.collider = BoxCollider(
    map_entity,
    center=Vec3(0, 7.8 + 5.5, 0),
    size=Vec3(110, 15.6, 95.5)
)
map_entity.collider.visible = True
map_entity.collider.color = color.rgba(0, 255, 0, 80)

invisible_floor = Entity(
    position=Vec3(-29, 9.5, -17.5),
    visible=False
)

invisible_floor.collider = BoxCollider(
    invisible_floor,
    center=Vec3(0, 0, 0),
    size=Vec3(52, 1, 33)
)
invisible_wall_1 = Entity(
    position=Vec3(45, 7, 5.5),
    visible=False
)

invisible_wall_1.collider = BoxCollider(
    invisible_wall_1,
    center=Vec3(0, 0, 0),
    size=Vec3(2, 4, 5)
)
enemy_walls.append(invisible_wall_1)

invisible_wall_2 = Entity(
    position=Vec3(37.5, 7, 2.5),
    visible=False
)

invisible_wall_2.collider = BoxCollider(
    invisible_wall_2,
    center=Vec3(0, 0, 0),
    size=Vec3(15, 4, 1)
)
enemy_walls.append(invisible_wall_2)
# wall3
invisible_wall_3 = Entity(
    position=Vec3(43.5, 6.5, 8),
    visible=False
)
invisible_wall_3.collider = BoxCollider(
    invisible_wall_3,
    center=Vec3(0, 0, 0),
    size=Vec3(1, 3, 1)
)
enemy_walls.append(invisible_wall_3)
# wall4
invisible_wall_4 = Entity(
    position=Vec3(32.5, 7, 7.6),
    visible=False
)
invisible_wall_4.collider = BoxCollider(
    invisible_wall_4,
    center=Vec3(0, 0, 0),
    size=Vec3(15, 4, 1)
)
enemy_walls.append(invisible_wall_4)
# wall5
invisible_wall_5 = Entity(
    position=Vec3(25, 7, 5),
    visible=False
)
invisible_wall_5.collider = BoxCollider(
    invisible_wall_5,
    center=Vec3(0, 0, 0),
    size=Vec3(1, 4, 4)
)
enemy_walls.append(invisible_wall_5)
# wall6（19,6,3 ~ 25,9,2）
invisible_wall_6 = Entity(
    position=Vec3(22, 7.5, 2.5),
    visible=False
)
invisible_wall_6.collider = BoxCollider(
    invisible_wall_6,
    center=Vec3(0, 0, 0),
    size=Vec3(6, 3, 1)
)
enemy_walls.append(invisible_wall_6)
# wall7
invisible_wall_7 = Entity(
    position=Vec3(24.5, 8, -16.75),
    visible=False
)
invisible_wall_7.collider = BoxCollider(
    invisible_wall_7,
    center=Vec3(0, 0, 0),
    size=Vec3(1, 4, 16.5)
)
enemy_walls.append(invisible_wall_7)
# wall8
invisible_wall_8 = Entity(
    position=Vec3(22, 8, -25.25),
    visible=False
)
invisible_wall_8.collider = BoxCollider(
    invisible_wall_8,
    center=Vec3(0, 0, 0),
    size=Vec3(4, 4, 1)
)
enemy_walls.append(invisible_wall_8)
# wall9
invisible_wall_9 = Entity(
    position=Vec3(11, 8, -26),
    visible=False
)
invisible_wall_9.collider = BoxCollider(
    invisible_wall_9,
    center=Vec3(0, 0, 0),
    size=Vec3(4, 4, 1)
)
enemy_walls.append(invisible_wall_9)
# wall10
invisible_wall_10 = Entity(
    position=Vec3(9, 8, -16.5),
    visible=False
)
invisible_wall_10.collider = BoxCollider(
    invisible_wall_10,
    center=Vec3(0, 0, 0),
    size=Vec3(1, 4, 17)
)
enemy_walls.append(invisible_wall_10)
# wall11
invisible_wall_11 = Entity(
    position=Vec3(-32, 12, -29.25),
    visible=False
)
invisible_wall_11.collider = BoxCollider(
    invisible_wall_11,
    center=Vec3(0, 0, 0),
    size=Vec3(28, 4, 1)
)
enemy_walls.append(invisible_wall_11)
# wall12
invisible_wall_12 = Entity(
    position=Vec3(-29.35, 12.25, -12.5),
    visible=False
)
invisible_wall_12.collider = BoxCollider(
    invisible_wall_12,
    center=Vec3(0, 0, 0),
    size=Vec3(28.7, 3.5, 1)
)
enemy_walls.append(invisible_wall_12)
# wall13
invisible_wall_13 = Entity(
    position=Vec3(-54, 12, -26.35),
    visible=False
)
invisible_wall_13.collider = BoxCollider(
    invisible_wall_13,
    center=Vec3(0, 0, 0),
    size=Vec3(1, 4, 14.7)
)
enemy_walls.append(invisible_wall_13)
# wall14（18,9,3 ~ 14,6,3）
invisible_wall_14 = Entity(
    position=Vec3(16, 7.5, 3),
    visible=False
)
invisible_wall_14.collider = BoxCollider(
    invisible_wall_14,
    center=Vec3(0, 0, 0),
    size=Vec3(4, 3, 1)
)
enemy_walls.append(invisible_wall_14)
# wall15（14,10,4.5 ~ -2,6,4）
invisible_wall_15 = Entity(
    position=Vec3(6, 8, 4.25),
    visible=False
)
invisible_wall_15.collider = BoxCollider(
    invisible_wall_15,
    center=Vec3(0, 0, 0),
    size=Vec3(16, 4, 1)
)
enemy_walls.append(invisible_wall_15)
# wall16（30,9,-4 ~ 30,6,2）
invisible_wall_16 = Entity(
    position=Vec3(30, 7.5, -1),
    visible=False
)
invisible_wall_16.collider = BoxCollider(
    invisible_wall_16,
    center=Vec3(0, 0, 0),
    size=Vec3(1, 3, 6)
)
enemy_walls.append(invisible_wall_16)
# wall17（30,9.5,-4 ~ 19,6,-4）
invisible_wall_17 = Entity(
    position=Vec3(24.5, 7.75, -4),
    visible=False
)
invisible_wall_17.collider = BoxCollider(
    invisible_wall_17,
    center=Vec3(0, 0, 0),
    size=Vec3(11, 3.5, 1)
)
enemy_walls.append(invisible_wall_17)
# wall18（14,8.7,-2.5 ~ 18,6,-2.5）
invisible_wall_18 = Entity(
    position=Vec3(16, 7.35, -2.5),
    visible=False
)
invisible_wall_18.collider = BoxCollider(
    invisible_wall_18,
    center=Vec3(0, 0, 0),
    size=Vec3(4, 2.7, 1)
)
enemy_walls.append(invisible_wall_18)
# wall19（2,9,-30 ~ 2,6,-40）
invisible_wall_19 = Entity(
    position=Vec3(2, 7.5, -35),
    visible=False
)
invisible_wall_19.collider = BoxCollider(
    invisible_wall_19,
    center=Vec3(0, 0, 0),
    size=Vec3(1, 3, 10)
)
enemy_walls.append(invisible_wall_19)
# wall20（13.5,9,-30 ~ 2,6,-30）
invisible_wall_20 = Entity(
    position=Vec3(7.75, 7.5, -30),
    visible=False
)
invisible_wall_20.collider = BoxCollider(
    invisible_wall_20,
    center=Vec3(0, 0, 0),
    size=Vec3(11.5, 3, 1)
)
enemy_walls.append(invisible_wall_20)
# wall21（12.5,9,-35.8 ~ 5.4,6,-35.7）
invisible_wall_21 = Entity(
    position=Vec3(8.95, 7.5, -35.75),
    visible=False
)
invisible_wall_21.collider = BoxCollider(
    invisible_wall_21,
    center=Vec3(0, 0, 0),
    size=Vec3(7.1, 3, 0.1)
)
enemy_walls.append(invisible_wall_21)


# wall22（13.8,9,-34.5 ~ 12.5,6,-35.7）
invisible_wall_22 = Entity(
    position=Vec3(13.15, 7.5, -35.1),
    visible=False
)
invisible_wall_22.collider = BoxCollider(
    invisible_wall_22,
    center=Vec3(0, 0, 0),
    size=Vec3(1.3, 3, 1.2)
)
enemy_walls.append(invisible_wall_22)


# wall23（13.8,9,-30 ~ 13.8,6,-34）
invisible_wall_23 = Entity(
    position=Vec3(13.8, 7.5, -32),
    visible=False
)
invisible_wall_23.collider = BoxCollider(
    invisible_wall_23,
    center=Vec3(0, 0, 0),
    size=Vec3(0.1, 3, 4)
)
enemy_walls.append(invisible_wall_23)


# wall24（5.4,9,-35.8 ~ 5.4,6,-38）
invisible_wall_24 = Entity(
    position=Vec3(5.4, 7.5, -36.9),
    visible=False
)
invisible_wall_24.collider = BoxCollider(
    invisible_wall_24,
    center=Vec3(0, 0, 0),
    size=Vec3(0.1, 3, 2.2)
)
enemy_walls.append(invisible_wall_24)


# wall25（5.7,9,-41.5 ~ 5.7,6,-40）
invisible_wall_25 = Entity(
    position=Vec3(5.7, 7.5, -40.75),
    visible=False
)
invisible_wall_25.collider = BoxCollider(
    invisible_wall_25,
    center=Vec3(0, 0, 0),
    size=Vec3(0.1, 3, 1.5)
)
enemy_walls.append(invisible_wall_25)


# wall26（9,9.5,-42 ~ 6.4,6,-42）
invisible_wall_26 = Entity(
    position=Vec3(7.7, 7.75, -42),
    visible=False
)
invisible_wall_26.collider = BoxCollider(
    invisible_wall_26,
    center=Vec3(0, 0, 0),
    size=Vec3(2.6, 3.5, 0.1)
)
enemy_walls.append(invisible_wall_26)


# wall27（8.7,9.8,-44 ~ 8.7,6,-43）
invisible_wall_27 = Entity(
    position=Vec3(8.7, 7.9, -43.5),
    visible=False
)
invisible_wall_27.collider = BoxCollider(
    invisible_wall_27,
    center=Vec3(0, 0, 0),
    size=Vec3(0.1, 3.8, 1)
)
enemy_walls.append(invisible_wall_27)


# wall28（11.8,9.8,-47.6 ~ 8.7,6,-44.5）
invisible_wall_28 = Entity(
    position=Vec3(10.25, 7.9, -46.05),
    visible=False
)
invisible_wall_28.collider = BoxCollider(
    invisible_wall_28,
    center=Vec3(0, 0, 0),
    size=Vec3(3.1, 3.8, 3.1)
)
enemy_walls.append(invisible_wall_28)


# wall29（19.5,9.7,-44.5 ~ 16.5,6,-47.5）
invisible_wall_29 = Entity(
    position=Vec3(18, 7.85, -46),
    visible=False
)
invisible_wall_29.collider = BoxCollider(
    invisible_wall_29,
    center=Vec3(0, 0, 0),
    size=Vec3(3, 3.7, 3)
)
enemy_walls.append(invisible_wall_29)


# wall30（19.5,9.7,-42.6 ~ 19.6,6,-44）
invisible_wall_30 = Entity(
    position=Vec3(19.55, 7.85, -43.3),
    visible=False
)
invisible_wall_30.collider = BoxCollider(
    invisible_wall_30,
    center=Vec3(0, 0, 0),
    size=Vec3(0.1, 3.7, 1.4)
)
enemy_walls.append(invisible_wall_30)


# wall31（22.6,9,-42.5 ~ 19.7,6,-42.5）
invisible_wall_31 = Entity(
    position=Vec3(21.15, 7.5, -42.5),
    visible=False
)
invisible_wall_31.collider = BoxCollider(
    invisible_wall_31,
    center=Vec3(0, 0, 0),
    size=Vec3(2.9, 3, 0.1)
)
enemy_walls.append(invisible_wall_31)


# wall32（22.7,9,-35.6 ~ 22.7,6,-42.4）
invisible_wall_32 = Entity(
    position=Vec3(22.7, 7.5, -39),
    visible=False
)
invisible_wall_32.collider = BoxCollider(
    invisible_wall_32,
    center=Vec3(0, 0, 0),
    size=Vec3(0.1, 3, 6.8)
)
enemy_walls.append(invisible_wall_32)


# wall33（19.4,9.5,-35.5 ~ 22.5,6,-35.5）
invisible_wall_33 = Entity(
    position=Vec3(20.95, 7.75, -35.5),
    visible=False
)
invisible_wall_33.collider = BoxCollider(
    invisible_wall_33,
    center=Vec3(0, 0, 0),
    size=Vec3(3.1, 3.5, 0.1)
)
enemy_walls.append(invisible_wall_33)


# wall34（19,9,-27.8 ~ 19,6,-35.4）
invisible_wall_34 = Entity(
    position=Vec3(19, 7.5, -31.6),
    visible=False
)
invisible_wall_34.collider = BoxCollider(
    invisible_wall_34,
    center=Vec3(0, 0, 0),
    size=Vec3(0.1, 3, 7.6)
)
enemy_walls.append(invisible_wall_34)


# wall35（9,10,-17 ~ 15,6,-17）
invisible_wall_35 = Entity(
    position=Vec3(12, 8, -17),
    visible=False
)
invisible_wall_35.collider = BoxCollider(
    invisible_wall_35,
    center=Vec3(0, 0, 0),
    size=Vec3(6, 4, 0.1)
)
enemy_walls.append(invisible_wall_35)
visible = True

# =====================
# 手動スポーン位置
# =====================
ENEMY_SPAWN_POINTS = [
    Vec3(14, 6.0, -21.7),
    Vec3(-9, 6.0, 2),
    Vec3(33, 6.0, 5.8),
    Vec3(-45, 10.0, -21),
]
ENEMY_VERTICAL_ATTACK_LIMIT = 1.2

# =====================
# 設定メニュー
# =====================
settings_open = False

settings_ui = Entity(
    parent=camera.ui,
    enabled=False
)

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
  global settings_open, game_paused
  settings_open = False
  game_paused = False
  settings_ui.enabled = False
  mouse.locked = True
  player.enabled = True

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
    scale=(0.25, 0.08),
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
# hit_sound.volume = 0.9
death_sound.volume = 1.0
footstep_sound.volume = 0.4

is_firing = False

# random.seed(0)
Entity.default_shader = lit_with_shadows_shader

# =====================
# プレイヤー
# =====================
player = FirstPersonController(
    origin_y=-.5,
    speed=8,
    collider='box'
)
player.position = (11, 5.5, -33)
player.rotation_y = 245
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))
player.is_dead = False
# =====================
# 被弾エフェクト
# =====================
player.hit_flash = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(275, 0, 0, 50),
    scale=(2, 2),
    enabled=False
)
player.mouse_sensitivity = Vec2(40, 40)
player.spawn_position = player.position
def respawn_here():
  pos = player.position
  rot = player.rotation

  player.collider = None   # ← まず外す

  player.position = pos + Vec3(-1, 0.05, 0)
  player.rotation = rot

  player.collider = BoxCollider(
      player,
      center=Vec3(0, 1, 0),
      size=Vec3(0.8, 2, 0.8)
  )


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

craft_table = Entity(
    model='cube',
    position=Vec3(-52.5, 10, -31.5),
    scale=Vec3(2, 1, 2),
    color=color.gray,
    collider='box'
)
craft_text = Text(
    parent=camera.ui,
    text='Press E to Craft Key',
    origin=(0, 0),
    scale=1.8,
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
# ミニマップ
# =====================
exit_dot = Entity(
    parent=minimap,   # ← 正解
    model='circle',
    color=color.lime,
    scale=0.03,
    z=-0.01,
    enabled=True
)
# =====================
# ミニマップ：鍵合成台
# =====================
craft_dot = Entity(
    parent=minimap,
    model='circle',
    color=color.yellow,
    scale=0.025,
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
    loop=True
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
    global enemy_key_drops
    if self.dead:
      return

    self.hp -= amount
    self.health_bar.scale_x = max(self.hp / 100 * 1.5, 0)

    if self.hp <= 0:
      self.dead = True
      # 鍵の破片ドロップ
      if enemy_key_drops < MAX_ENEMY_KEY_DROPS and random.random() < 0.3:
        KeyFragment(self.world_position)
        enemy_key_drops += 1

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

  def update(self):
    if game_paused or self.dead or player.is_dead:
      return

    # プレイヤーとの水平距離
    to_player = player.position - self.position
    dist = Vec2(to_player.x, to_player.z).length()

    # =====================
    # 範囲外
    # =====================
    if dist > ENEMY_DETECT_RADIUS:
      self.rotation_z = 0
      self.rotation_x = 0
      self.attack_timer -= time.dt
      return

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
      move_amount = self.speed * time.dt

      hit = raycast(
          self.world_position + Vec3(0, 1, 0),
          self.forward,
          distance=move_amount + 0.3,
          ignore=(self, player)
      )
      if not hit.hit:
        self.position += self.forward * move_amount

      self.walk_time += time.dt * 3
      self.rotation_z = sin(self.walk_time) * 2
      self.y = self.base_y + sin(self.walk_time * 2) * 0.05
      self.rotation_x = 8
    else:
      self.rotation_z = 0
      self.rotation_x = 0

      # 高さチェック
      height_diff = player.y - self.y
      if height_diff > ENEMY_VERTICAL_ATTACK_LIMIT:
        return

      # 攻撃
      self.attack_timer -= time.dt
      if self.attack_timer <= 0:
        self.attack_timer = ENEMY_ATTACK_COOLDOWN
        self.attack_player()

  def attack_player(self):
    if player.hp <= 0:
      return
    # hit_sound.play()

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
    position=(42, 5, 8.5),
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
  global has_key, enemy_key_drops
  if game_paused:
    return
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

  # 既存の update() の中に追加
  if distance(player.position, craft_table.position) < 2.5:
    craft_text.enabled = True
    craft_text.position = (0, -0.2)

    if key_fragments >= KEY_FRAGMENTS_NEEDED and not has_key:
      craft_text.text = 'Press E to CRAFT KEY'
      craft_text.color = color.lime

      if held_keys['e']:
        has_key = True
        key_text.text = 'Key: COMPLETE'
        key_text.color = color.lime
    else:
      craft_text.text = 'Need Key Fragments'
      craft_text.color = color.orange
  else:
    craft_text.enabled = False

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
  # =====================
  # Key READY 点滅演出
  # =====================
  if key_text.text == 'Key: READY':
    key_text.alpha = 0.6 + abs(sin(time.time() * 3)) * 0.4
  else:
    key_text.alpha = 1


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
  player.position = (11, 5.5, -33)
  player.rotation_y = 245

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
  # 出口
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
  # 鍵合成台
  # =====================
  dx = craft_table.x - player.x
  dz = craft_table.z - player.z

  world_dist = math.sqrt(dx * dx + dz * dz)

  rx = dx * math.cos(angle) - dz * math.sin(angle)
  rz = dx * math.sin(angle) + dz * math.cos(angle)

  CRAFT_DOT_RADIUS = 0.015
  max_r = MINIMAP_RADIUS - CRAFT_DOT_RADIUS - FRAME_MARGIN

  map_dist = world_dist * MINIMAP_SCALE

  if map_dist <= max_r:
    x = rx * MINIMAP_SCALE
    y = rz * MINIMAP_SCALE
  else:
    length = math.sqrt(rx * rx + rz * rz)
    if length != 0:
      rx /= length
      rz /= length
    x = rx * max_r
    y = rz * max_r

  craft_dot.enabled = True
  craft_dot.position = (x, y)


# =====================
# 敵生成関数
# =====================
def spawn_enemy(per_spawn=3):
  for base_pos in ENEMY_SPAWN_POINTS:
    for _ in range(per_spawn):
      if len(enemies) >= MAX_ENEMIES:
        return

      offset = Vec3(
          random.uniform(-2, 2),
          0,
          random.uniform(-2, 2)
      )

      e = Enemy(position=base_pos + offset)
      enemies.append(e)
      register_enemy(e)


# 初期スポーン
spawn_enemy(3)

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

game_paused = False

def input(key):
  global is_firing, gun_sound_playing, is_ads, settings_open, game_paused

  # ===== ESC メニュー =====
  if key == 'escape':
    settings_open = not settings_open
    game_paused = settings_open
    settings_ui.enabled = settings_open

    if settings_open:
      mouse.locked = False
      player.enabled = False
    else:
      mouse.locked = True
      player.enabled = True
  # ===== 射撃 =====
  if key == 'left mouse down' and not game_paused:
    is_firing = True

  if key == 'left mouse up':
    is_firing = False
    gun_sound.stop()
    gun_sound_playing = False

  # ===== ADS =====
  if key == 'right mouse down' and not game_paused:
    is_ads = True

  if key == 'right mouse up':
    is_ads = False

  # ===== リロード =====
  if key == 'r' and not game_paused:
    reload()

  # ===== リスポーン =====
  if key == 'f' and dead_ui.enabled:
    respawn_player()

  if key == 'z':
    respawn_here()

app.run()
