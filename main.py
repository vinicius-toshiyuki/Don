from Parser import *
from Game import *

parser = Parser()

items = parser.get_items()
creatures = parser.get_creatures()
player = parser.get_player()
maps = parser.get_maps()
    
units = {
        "player" : player,
        "creatures" : creatures
        }

g = Game(units, maps, items)
g.mainloop()
