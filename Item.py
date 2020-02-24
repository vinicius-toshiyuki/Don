class __Item:
    def __init__(s, name, **attr):
        s._name = name
        s._count = 0
        s._attr = attr

    def count(s):
        return s._count

    def is_empty(s):
        return s._count == 0

    def increase(s, value):
        if (value := int(value)) > 0:
            s._count += value
        return s

    def decrease(s, value):
        if (value := int(value)) >= s._count:
            s._count -= value
            i = type(s)(str(s))
            i.increase(value)
            return i
        return None

    def is_consumable(s):
        return False

    def __str__(s):
        return s._name

class __Consumable(__Item):
    def is_consumable(s):
        return True

    def consume(s, unit):
        return unit.take_item(str(s)) is not None

class __HealingItem(__Consumable):
    def consume(s, unit):
        unit.heal(s._attr["healing"])
        super().consume(unit)

class Herb(__HealingItem):
    pass

class Fruit(__HealingItem):
    pass

class Fur(__Item):
    pass
