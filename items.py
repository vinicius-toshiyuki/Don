class Item:
    _consumable = False

    def is_consumable(self=None):
        return Item._consumable

    def configure():
        pass

class Consumable(Item):
    _consumable = True

    def is_consumable(self=None):
        return Consumable._consumable

class Herb(Consumable):
    __instance = None
    _regen = None
        
    def get_instance():
        if Herb.__instance is None:
            Herb()
        return Herb.__instance
        
    def __init__(self):
        if Herb.__instance is None:
            Herb.__instance = self
        else:
            raise Exception('Herb is singleton!')

    def configure(regen):
        if (regen := int(regen)) > 0:
            Herb._regen = regen

    def consume(self, unit):
        if unit.take_item(self)[1] > 0: 
            unit.recover(Herb._regen)

    def __str__(self):
        return self.__class__.__name__

class Fruit(Consumable):
    __instance = None
    _regen = None
        
    def get_instance():
        if Fruit.__instance is None:
            Fruit()
        return Fruit.__instance
        
    def __init__(self):
        if Fruit.__instance is None:
            Fruit.__instance = self
        else:
            raise Exception('Fruit is singleton!')

    def configure(regen):
        if (regen := int(regen)) > 0:
            Fruit._regen = regen

    def consume(self, unit):
        if unit.take_item(self)[1] > 0: 
            unit.recover(Fruit._regen)

    def __str__(self):
        return self.__class__.__name__

class Fur(Item):
    __instance = None
        
    def get_instance():
        if Fur.__instance is None:
            Fur()
        return Fur.__instance

    def __init__(self):
        if Fur.__instance is None:
            Fur.__instance = self
        else:
            raise Exception('Fur is singleton!')

    def __str__(self):
        return self.__class__.__name__
