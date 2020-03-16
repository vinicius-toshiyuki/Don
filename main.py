from Parser import *
from Game import *

parser = Parser()

items = parser.get_items('data/item.xml')
creatures = parser.get_creatures('data/unit.xml')
player = parser.get_player('data/unit.xml')
maps = parser.get_maps('data/map.xml')
    
units = {
        "player" : player,
        "creatures" : creatures
        }

g = Game(units, maps, items)
g.mainloop()
