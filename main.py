from src.components.window import *
from src.game.scenes.scene1 import *

game = MainWindow(dev_mode)

scene1 = Scene1(game)

game.activate_scene('Scene1')

game.run()