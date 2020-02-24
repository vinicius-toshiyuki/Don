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
        s._level = level
        s._exp = exp
        s._exp_to_next = exp_to_next

    def grant_exp(s, value):
        value = int(value)
        if value > 0:
            s._exp += value
            if s._exp_to_next <= s._exp:
                s._exp -= s._exp_to_next
                s._level_up()

    def _level_up(s):
        s._level += 1
        s._exp_to_next = int((s._level * 0.05 + 2) * s._exp_to_next)

        atts = (s._max_life, s._attack, s._defense, s._agility)
        new_atts = []
        for att in atts:
            prob = 75 - int(0.3 * s._level)
            while rand() % 100 < prob:
                prob /= 2
                att += 1
            new_atts.append(att)

        s._max_life = new_atts[0]
        s._attack = new_atts[1]
        s._defense = new_atts[2]
        s._agility = new_atts[3]

        s.heal(s._max_life * 0.2)

        return s._exp_to_next

    def get_stats(s):
        data = super().get_stats()
        data.update({
            "Experience" : s._exp,
            "Exp needed to next LVL" : s._exp_to_next
            })
        return data

class Creature(Actor):
    def exp_value(s):
        return int((s._max_life + s._attack + s._defense + s._agility) * 0.077)

class Dummy(Unit):
    pass
