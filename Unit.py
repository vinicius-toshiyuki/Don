from random import randint as rand

class Unit:
    def __init__(s, name, items):
        s._name = name
        s._items = items

    def get_items(s):
        return s._items

    def get_consumables(s):
        return list(filter(lambda i:
            i.is_consumable(),
            s._items
            ))

    def take_item(s, name, quantity=1):
        try:
            item = next(filter(lambda i:
                str(i) == name,
                s._items
                ))
            if (i := item.decrease(quantity)) is not None:
                if item.is_empty():
                    s._items.pop(s._items.index(item))
                return i
        except:
            pass
        return None

    def give_item(s, item):
        if not item.is_empty():
            try:
                i = next(filter(lambda i:
                    str(i) == str(item),
                    s._items
                    ))
                i.increase(item.count())
            except:
                s._items.append(item)


    def get_stats(s):
        return {
                "Name" : s._name
                }

    def __str__(s):
        return s._name

class Actor(Unit):
    def __init__(s, name, items, max_health, health, attack, defense, agility):
        super().__init__(name, items)
        s._max_health = int(max_health)
        s._health = int(health)
        s._attack = int(attack)
        s._defense = int(defense)
        s._agility = int(agility)

        s._guard = False

    def is_alive(s):
        return s._health > 0

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
        s._health = min(s._max_health, s._health + int(value))

    def guard(s):
        s._guard = True

    def unguard(s):
        s._guard = False

    def get_stats(s):
        data = super().get_stats()
        data.update({
                "Name" : s._name,
                "Health" : (s._health, s._max_health),
                "Attack" : s._attack,
                "Defense" : s._defense,
                "Agility" : s._agility,
                })
        return data

class Human(Actor):
    pass

class Player(Human):
    def __init__(s, name, items, max_health, health, attack, defense, agility, level, exp, exp_to_next):
        super().__init__(name, items, max_health, health,attack, defense, agility)
        s._level = int(level)
        s._exp = int(exp)
        s._exp_to_next = int(exp_to_next)

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

    def get_stats(s):
        data = super().get_stats()
        data.update({
            "Level" : s._level,
            "Experience" : s._exp,
            "Exp needed to next LVL" : s._exp_to_next
            })
        return data

class Creature(Actor):
    pass

class Dummy(Unit):
    pass
