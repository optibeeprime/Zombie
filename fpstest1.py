from ursina import *

app = Ursina()

e = Entity(model='zombie')
print(e.animations)

app.run()
