class Log:
    _queue = list()
    _tag_log = dict()
    
    def log(message, tag=None):
        if tag is None:
            Log._queue.append(message)
        elif tag in Log._tag_log:
            Log._tag_log[tag].append(message)
        else:
            Log._tag_log[tag] = [message]
    
    def flush():
        while len(Log._queue) > 0:
            print(Log._queue.pop(0))

        for t in Log._tag_log:
            print("\n", t)
            while len(Log._tag_log[t]) > 0:
                print(Log._tag_log[t].pop(0))
        Log._tag_log = dict()

class Unit:
    def __init__(self, name, level, life, attack, defense, agility, items):
        self.name = name
        self.level = int(level)
        self.max_life = int(life)
        self.life = int(life)
        self.attack = int(attack)
        self.defense = int(defense)
        self.agility = int(agility)
        self._last_hit = None
        self._guard = False
        self._items = dict(items)

        module = __import__("items")
        self._items = dict([(getattr(module, i).get_instance(), self._items[i]) for i in self._items])

    def alive(self):
        return self.life > 0

    def take_damage(self, damage=None):
        if damage is not None:
            self._last_hit = max(
                    0 if self._guard else 1, 
                    damage - self.defense * (2 if self._guard else 1)
                    )
            self._guard = False
            self.life -= self._last_hit
            self.life = max(self.life, 0)
        return self._last_hit

    def recover(self, value):
        self.life = min(self.max_life, self.life + max(int(value), 0))

    def calc_damage(self):
        return self.attack

    def stats(self):
        return {
                "Name" : self.name,
                "Level" : self.level,
                "Max life" : self.max_life,
                "Life" : self.life,
                "Attack" : self.attack,
                "Defense" : self.defense,
                "Agility" : self.agility
                }

    def run(self, foe):
        if self.agility / foe.agility > 0.1:
            diff = abs(self.agility - foe.agility)
            if foe.agility > self.agility:
                return chance(diff * 5)
            else:
                return chance(diff * 7 + int(0.1 * foe.agility) * 5)
        return False

    def guard(self):
        self._guard = True

    def unguard(self):
        self._guard = False

    def get_items(self):
        return list(self._items.keys())

    def get_consumables(self):
        return list(filter(lambda i: i.is_consumable(), self._items.keys()))

    def get_item_count(self, item):
        if item in self._items:
            return self._items[item]
        return 0

    def take_item(self, name, quantity=1):
        if name in self._items and self._items[name] >= quantity:
            self._items[name] -= quantity
            if self._items[name] == 0:
                self._items.pop(name)
            return (name, quantity)
        return (name, 0)

    def give_item(self, name, quantity=1):
        if quantity < 1:
            return

        if name in self._items:
            self._items[name] += quantity
        else:
            self._items[name] = quantity

    def give_bundle(self, bundle):
        for b in bundle:
            self.give_item(*b)

    def __str__(self):
        return self.name

class Player(Unit):
    def __init__(self, *args):
        super().__init__(*args)
        self._exp = 0
        self._exp_to_next = 12
        self.money = 500

    def grant_exp(self, value, source=None):
        if value > 0:
            Log.log("{} received {} experience".format(self, value), source)
            self._exp += value
            Log.log("Exp: {}/{}".format(self._exp, self._exp_to_next), source)
            if self._exp_to_next <= self._exp:
                self._exp -= self._exp_to_next
                self._level_up()

    def _level_up(self):
        self.level += 1
        Log.log("Level up! {} -> {}".format(self.level - 1, self.level), "Stats")
        self._exp_to_next = int((self.level * 0.05 + 2) * self._exp_to_next)

        atts = (self.max_life, self.attack, self.defense, self.agility)
        new_atts = []
        for att in atts:
            prob = 75 - int(0.3 * self.level)
            while chance(prob):
                prob /= 2
                att += 1
            new_atts.append(att)

        Log.log("Life: {} -> {}".format(atts[0], new_atts[0]), "Stats")
        Log.log("Attack: {} -> {}".format(atts[1], new_atts[1]), "Stats")
        Log.log("Defense: {} -> {}".format(atts[2], new_atts[2]), "Stats")
        Log.log("Agility: {} -> {}".format(atts[3], new_atts[3]), "Stats")
        self.max_life = new_atts[0]
        self.attack = new_atts[1]
        self.defense = new_atts[2]
        self.agility = new_atts[3]

        self.recover(self.max_life * 0.33)

        return self._exp_to_next

    def stats(self):
        data = super().stats()
        data.update({
            "Experience" : self._exp,
            "Exp needed to next LVL" : self._exp_to_next
            })
        return data


class Monster(Unit):
    def exp_value(self):
        return int(self.level * (self.max_life + self.attack + self.defense + self.agility) * 0.1)

    def take_item(self, name):
        count = 0
        if name in self._items:
            prob = self._items[name]
            while chance(prob):
                prob /= 3
                count += 1
        return (name, count)

    def drop_items(self):
        drop = []
        for i in self._items:
            drop.append(self.take_item(i))
        return drop

    def give_item(self, name, prob):
        if name not in self._items:
            self._items[name] = prob
        else:
            raise Exception("{} already has {}!".format(self, name)) 

class Map:
    monsters = None
    def __init__(self, type, connections, chance, monsters):
        self.type = type
        self.chance = int(chance)
        self._base_chance = self.chance
        self.monsters = monsters
        self.connections = connections

    def rand_monster(self):
        return Map.monsters[choice(self.monsters)]

    def encounter(self, unit):
        if rand(1,100) <= self.chance and len(self.monsters) > 0:
            self.chance = self._base_chance
            monster = copy.copy(self.rand_monster())
            Log.log("{} encountered a {}".format(unit, monster), "Battle")
            units = [unit, monster]
            units.sort(reverse=True, key=lambda k: k.agility)
            Log.log("{} goes first".format(units[0]), "Battle")
            if (r := fight(*units)) == unit:
                unit.grant_exp(monster.exp_value(), "Battle")
                drop = monster.drop_items()
                for d in drop:
                    if d[1] > 0:
                        Log.log("{} has dropped {} {}".format(monster, *d[::-1]), "Battle")
                unit.give_bundle(drop)
            return True
        self.chance += self.chance * 0.05
        return False

    def __str__(self):
        return self.type

class Game:
    def __init__(self, player, monsters, maps, gitems):
        self.player = player
        Map.monsters = monsters
        self.maps = maps
        self._items = gitems
        self.__leave_default = 1
        self.__m = self.maps['1']

    def mainloop(self):
        while True:
            clear()
            Log.flush()
            Log.log("{} entered a {}".format(self.player, self.__m))
            if self.__m.encounter(self.player) and not self.player.alive():
                Log.flush()
                Log.log("Game over")
                Log.flush()
                break
            self.action()
        
    def action(self):
        Log.flush()
        if (i := prompt(
            "Take an action:",
            {
                1 : "Wait",
                2 : "Walk",
                3 : "Stats",
                4 : "Bag"
            }, 1)) == 1:
                pass
        elif i == 2:
            self.change_map()
        elif i == 3:
            for s in (stats := self.player.stats()):
                Log.log("{}: {}".format(s, stats[s]), "Stats")
            Log.flush()
            self.action()
        elif i == 4:
            if (j := prompt(
                    "Choose a consumable item:",
                    ["Go back"] + ["{} ({})".format(c, self.player.get_item_count(c)) for c in self.player.get_items()],
                    valid=[1] + [self.player.get_items().index(i) + 2 for i in self.player.get_consumables()]
                    )) != 1:
                cons = self.player.get_items()[j-2]
                cons.consume(self.player)
                Log.log("{} consumed a {}".format(self.player, cons))

            self.action()

    def change_map(self):
        i = prompt("Where to go?", dict([(o, self.maps[o]) for o in self.__m.connections]))
        Log.log("{} left the {}".format(self.player, self.__m))
        self.__m = self.maps[i]

def right_input(text=None, options=None, default=None):
    if text is not None:
        if default is not None:
            text += "[{}]".format(default)
        text += ' '
    if options is None:
        while (i := input(text if text is not None else '')) != '':
            if default is not None and i == '':
                i = default
                break
        return i
    while (i := input(text if text else '')) not in [str(o) for o in options]:
        if i == '' and default in options:
            i = default
            break
        print("Invalid option!")
    return type(list(options)[0])(i)

def chance(percentage):
    return rand(0, 99) < int(percentage)

def prompt(header, options, default=None, valid=None):
    if type(options) != dict:
        options = dict(enumerate(options, 1))
    print("\n", header)
    for o in options:
        print("[{}] {}".format(o, options[o]))
    return right_input("Option:", options.keys() if valid is None else valid, default)

def clear():
    print("\033[2J\033[0;0H")

def fight(u1, u2):
    if not u1.alive():
        return u2
    if not u2.alive():
        return u1
    
    Log.flush()
    
    default = 1
    if type(u1) == Player:
        i = prompt(
                "What will {} do?".format(u1),
                {
                    1 : "Fight",
                    2 : "Guard",
                    3 : "Run",
                    4 : "Use item"
                }, default
        )
        default = i
        clear()
    else:
        i = rand(0, 2) % 2 + 1

    if  i == 1:
        Log.log("{} hit {} for {} damage".format(u1, u2, u2.take_damage(u1.calc_damage())), "Battle")
        Log.log("{} has {}/{} life remaining".format(u2, u2.life, u2.max_life), "Battle")
    elif i == 2:
        u1.guard()
        Log.log("{} is on guard!".format(u1), "Battle")
    elif i == 3:
        if u1.run(u2):
            Log.log("{} ran away from combat".format(u1), "Battle")
            Log.log("{} is now sad and alone".format(u2), "Battle")
            return None
        else:
            Log.log("{} tried to run away but failed!".format(u1), "Battle")
    elif i == 4:
        if (j := prompt(
                "Choose item:",
                ["Go back"] + ["{} ({})".format(c, u1.get_item_count(c)) for c in u1.get_consumables()]
                )) == 1:
            return fight(u1, u2)
        else:
            cons = u1.get_consumables()[j-2]
            cons.consume(u1)
            Log.log("{} consumed a {}".format(u1, cons), "Battle")
    u2.unguard()
    return fight(u2, u1)

import xml.etree.ElementTree as ET
from random import randint as rand, choice
import copy
tree = ET.parse('data.xml')
data = tree.getroot()

monsters = {}
for unit in data.iter("unit"):
    unittype = unit.attrib["type"]
    if unittype == "player": 
        player = Player(*[i.text for i in unit], [])
    elif unittype == "monster":
        monsters[list(unit.iter("name"))[0].text] = Monster(*[i.text for i in unit][:6], dict([(i.text, int(i.attrib["prob"])) for i in list(unit.iter("inventory"))[0]]))

maps = {}
for mapdata in data.iter("map"):
    maps[mapdata.attrib["id"]] = Map(
            list(mapdata.iter("type"))[0].text,
            [c.text for c in list(mapdata.iter("connection"))[0]],
            list(mapdata.iter("chance"))[0].text,
            [m.text for m in (list(mapdata.iter("monster")) + [[]])[0]]
            )

gameitems = dict()
module = __import__("items")
for it in data.iter("item"):
    iclass = getattr(module, it.attrib["name"])
    gameitems[it.attrib["name"]] = iclass.get_instance()
    iclass.configure(*[i.text for i in it])
    
g = Game(player, monsters, maps, gameitems)
g.mainloop()
