from Parser import *
from Game import *

parser = Parser()

items = parser.get_items('item.xml')
creatures = parser.get_creatures('unit.xml')
player = parser.get_player('unit.xml')
maps = parser.get_maps('map.xml')
    
units = {
        "player" : player,
        "creatures" : creatures
        }

g = Game(units, maps, items)
g.mainloop()
