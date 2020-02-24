import xml.etree.ElementTree as ET
from random import randint as rand
import copy
from Unit import *
from Item import *
from Map import *

class Parser:
    def __init__(s):
        s.__module = __import__("Item")
        s._parsed_items = dict()
        s._parsed_creatures = dict()
        s._parsed_maps = dict()

    def get_player(s, unit_path="unit.xml"):
        s._units = ET.parse(unit_path).getroot()
        p = s._units.find("player")
        return Player(
                p.get("name"),
                s._get_player_items(p),
                p.find("life").get("max_value"),
                p.find("life").get("value"),
                p.find("attack").get("value"),
                p.find("defense").get("value"),
                p.find("agility").get("value"),
                p.find("level").get("value"),
                p.find("experience").get("value"),
                p.find("experience").get("to_next")
                )
    def _get_player_items(s, p):
        return list(map(lambda i:
            copy.copy(s._parsed_items[i.get("name")]).increase(int(i.get("quantity"))),
            p.findall("inventory/item")
            ))

    def get_creatures(s, unit_path="unit.xml"):
        s._units = ET.parse(unit_path).getroot()
        creatures = s._units.findall("creature")
        s._parsed_creatures = dict(map(lambda c:
            (c.get("name"), Creature(
                c.get("name"),
                s._get_creature_items(c),
                c.find("life").get("max_value"),
		c.find("life").get("value"),
		c.find("attack").get("value"),
		c.find("defense").get("value"),
		c.find("agility").get("value")
                )),
            creatures
            ))
        return s._parsed_creatures
    def _get_creature_items(s, c):
        return list(map(lambda i:
            copy.copy(s._parsed_items[i.get("name")]).increase(s.__get_drop_quantity(int(i.get("drop_rate")))),
            c.findall("inventory/item")
            ))
    def __get_drop_quantity(s, drop_rate):
        count = 0
        while rand(0, 99) < drop_rate:
            drop_rate = int(drop_rate / 2.5)
            count += 1
        return count

    def get_maps(s, map_path="map.xml"):
        s._maps = ET.parse(map_path).getroot()
        maps = s._maps.findall("map")
        s._parsed_maps = dict(map(lambda m:
            (m.get("name"), Map(
                m.get("name"),
                m.get("encounter_rate"),
                s._get_map_connections(m),
                s._get_map_units(m)
                )),
            maps
            ))
        return s._parsed_maps
    def _get_map_connections(s, m):
        return list(map(lambda c:
            c.get("to"),
            m.findall("connection")
            ))
    def _get_map_units(s, m):
        pairs = tuple(map(lambda u:
            (u.get("type"),
                (
                    u.get("name"),
                    copy.copy(s._parsed_creatures[u.get("name")]))
                ),
            m.findall("unit")
            ))
        units = dict()
        for t, n in pairs:
            if t in units:
                units[t].append(n)
            else:
                units[t] = [n]
        for t in units:
            units[t] = dict(units[t])
        return units

    def get_items(s, item_path="item.xml"):
        s._items = ET.parse(item_path).getroot()
        items = s._items.findall("item")

        s._parsed_items = dict(map(lambda i:
            (i.get("name"), getattr(s.__module, i.get("name"))(
                i.get("name"),
                **dict([(a.get("name"), a.get("value")) for a in i.findall("attribute")])
                )),
            items
            ))
        return s._parsed_items
"""
p = Parser()
items = p.get_items()
print(items)
player = p.get_player()
print(player.stats())
creatures = p.get_creatures()
print(creatures)
maps = p.get_maps()
print(maps)
"""
