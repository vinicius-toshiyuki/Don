from random import randint as rand
from Inventory import *
import warnings

class Unit:
    def __init__(s, name, inventory):
        s._name = name
        s._inventory = inventory

    @property
    def inventory(s): return s._inventory
    @property
    def name(s): return s._name
    @property
    def stats(s): return { "Name" : s._name }

    def __str__(s):
        return s._name

class Actor(Unit):
    def __init__(s, name, inventory, max_health, health, attack, defense, agility):
        super().__init__(name, inventory)
        s._max_health = int(max_health)
        s._health = int(health)
        if s._health > s._max_health:
            s._health = s._max_health
            warnings.warn('health greater than max_health, capping to max_health', Warning)
        s._attack = int(attack)
        s._defense = int(defense)
        s._agility = int(agility)

        if any([x <= 0 for x in (s._max_health,s._attack,s._defense,s._agility)]):
            raise ValueError('Invalid value: value less than or equal to zero')

        s._guard = False

    @property
    def max_health(s): return s._max_health
    @property
    def health(s): return s._health
    @property
    def attack(s): return s._attack
    @property
    def defense(s): return s._defense
    @property
    def agility(s): return s._agility

    def exp_value(s):
        return int((s._max_health + s._attack + s._defense + s._agility) * 0.15)

    def get_damage(s):
        return s._attack

    def take_damage(s, value):
        value = int(value)
        value = int(max(
                0 if s._guard else 1, 
                value - s._defense * (1.5 if s._guard else 1)
                ))
        s._guard = False
        s._health = max(s._health - value, 0)
        return value

    def heal(s, value):
        if int(value) < 0:
            raise ValueError('Invalid value: heal value must be greater than 0')
        s._health = min(s._max_health, s._health + int(value))

    def guard(s):
        s._guard = True

    def unguard(s):
        s._guard = False

    def run(s, u):
        if s._agility / u.agility > 0.1:
            diff = abs(s._agility - u.agility)
            if u.agility > s._agility:
                return rand(0, 99) < diff * 5
            else:
                return rand(0, 99) < (diff * 7 + int(0.1 * u.agility * 5))
        return False

    def use_item(s, name):
        if type(name) == str:
            item = s._inventory.take(name)
        else:
            item = name
        for att in item.attrib:
            __var__ = []
            exec('__var__.append(item.'+att+'())', {}, {'__var__' : __var__, 'item' : item})
            exec(__var__[0].format('s'))

    @property
    def stats(s):
        return {
                "Name" : s._name,
                "Health" : (s._health, s._max_health),
                "Attack" : s._attack,
                "Defense" : s._defense,
                "Agility" : s._agility,
                }

class Human(Actor):
    pass

class Player(Human):
    def __init__(s, name, inventory, max_health, health, attack, defense, agility, level, exp, exp_to_next):
        super().__init__(name, inventory, max_health, health,attack, defense, agility)
        s._level = int(level)
        s._exp = int(exp)
        s._exp_to_next = int(exp_to_next)
        if s._exp >= s._exp_to_next:
            raise ValueError('Invalid exp value: must be less than exp_to_next')
        if s._exp < 0:
            raise ValueError('Invalid value: must be greater than 0')
        elif s._level <= 0 or s._exp_to_next <= 0:
            raise ValueError('Invalid value: must be greater than 0 or equal')

    @property
    def level(s): return s._level
    @property
    def exp(s): return s._exp
    @property
    def exp_to_next(s): return s._exp_to_next

    def grant_exp(s, value):
        value = int(value)
        if value > 0:
            s._exp += value
            att_change = None
            while s._exp_to_next <= s._exp:
                s._exp -= s._exp_to_next
                if att_change is None:
                    att_change = s._level_up()
                else:
                    changed = s._level_up()
                    for att in changed:
                        if att in att_change:
                            att_change[att] += changed[att]
                        else:
                            att_change[att] = changed[att]
            return att_change
        return None

    def _level_up(s):
        s._exp_to_next = int((s._level * 0.05 + 2) * s._exp_to_next)

        atts = ("Health", "Attack", "Defense", "Agility")
        att_change = {"Level" : 1}
        for att in atts:
            prob = 75 - int(0.3 * s._level)
            att_change[att] = 0
            while rand(0, 99) < prob:
                prob /= 2
                att_change[att] += 1
            if att_change[att] == 0:
                att_change.pop(att)

        s._level += 1
        s._max_health += att_change["Health"] if "Health" in att_change else 0
        s._attack += att_change["Attack"] if "Attack" in att_change else 0
        s._defense += att_change["Defense"] if "Defense" in att_change else 0
        s._agility += att_change["Agility"] if "Agility" in att_change else 0

        s.heal(s._max_health * 0.2)

        return att_change

    @property
    def stats(s):
        data = super().stats
        data.update({
            "Level" : s._level,
            "Experience" : s._exp,
            "Exp needed to next LVL" : s._exp_to_next
            })
        return data

class Creature(Actor):
    def __init__(s, name, inventory, max_health, health, attack, defense, agility, drop_rates):
        super().__init__(name, inventory, max_health, health, attack, defense, agility)
        s._drop_rates = drop_rates

    @property
    def drop_rates(s):
        return dict(s._drop_rates)

class Dummy(Unit):
    pass
