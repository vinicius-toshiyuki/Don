from Parser import *
from Game import *
import Widget.Manager as wm

parser = Parser()

items = parser.get_items('item.xml')
creatures = parser.get_creatures('unit.xml')
player = parser.get_player('unit.xml')
maps = parser.get_maps('map.xml')
    
units = {
        "player" : player,
        "creatures" : creatures
        }

m = wm.Manager()
m.background()
g = Game(m, units, maps, items)
g.mainloop()
