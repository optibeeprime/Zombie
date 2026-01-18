from ursina import *
from pathlib import Path

# ★ 先に assets を指定する（超重要）
application.asset_folder = Path('assets')

app = Ursina()

print('asset_folder:', application.asset_folder)
print('Walking model:', load_model('Walking'))
print('attack model:', load_model('attack'))
print('die model:', load_model('die'))

Entity(
    model='Walking',
    scale=1,
    rotation=(0, 180, 0),
)

EditorCamera()
Sky()

app.run()
