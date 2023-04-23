#from build.game.scenes.scene01 import *
from src.components.map.map import *

game = MainWindow(dev_mode)

scene1 = Scene1(game)

game.activate_scene('Scene1')

game.run()
