from ursina import *
from pathlib import Path

application.asset_folder = Path('assets')
app = Ursina()

print('custom obj:', load_model('test'))

Entity(
    model='test',
    scale=1,
)

EditorCamera()
Sky()
app.run()
