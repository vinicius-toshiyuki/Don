class __Item:
    def __init__(s, name):
        s._name = name

    @property
    def consumable(s): return False
    @property
    def name(s): return s._name

    def __str__(s):
        return s._name

class __Consumable(__Item):
    def __init__(s, name, **attrib):
        super().__init__(name)
        s._attrib = attrib

    @property
    def consumable(s):
        return True

    @property
    def attrib(s): return dict(s._attrib)

class Herb(__Consumable):
    def healing(s):
        return '__var__ = {};' + \
                '__var__.heal({})'.format(s._attrib['healing'])

class Fruit(__Consumable):
    def healing(s):
        return '__var__ = {};' + \
                '__var__.heal({})'.format(s._attrib['healing'])

class Fur(__Item):
    pass
