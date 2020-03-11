import utils

class Inventory:
    # {name : item}
    _items = {}
    __set = False
    def __init__(s):
        if Inventory.__set:
            # {name : (count, item)}
            s._items = {}
        else:
            raise Exception('Inventory class items not set: call Inventory.set')

    @property
    def items(s):
        return tuple(str(v[1]) for v in s._items.values())

    def set(items):
        Inventory.__set = True
        Inventory._items = items

    def has(s, name):
        return name in s._items

    def count(s, name):
        if s.has(name):
            return s._items[name][0]
        return 0

    @utils.typecheck(None, str, count=int)
    def take(s, name, count=1):
        if count < 1:
            raise ValueError('invalid value: count must be greater than 0')
        if s.count(name) >= count:
            ret = s._items[name][1]
            if s._items[name][0] == count:
                s._items.pop(name)
            else:
                s._items[name] = (s._items[name][0] - count, ret)
            return ret if count == 1 else (count, ret)
        else:
            raise Exception('Inventory does not have {}'.format(name))

    def put(s, item):
        if type(item) == tuple:
            count = int(item[0])
            name = str(item[1])
        else:
            name = str(item)
            count = 1
        if count <= 0:
            raise ValueError('count must be greater than 0')

        s._items[name] = ((s._items[name][0] if s.has(name) else 0) + count, Inventory._items[name])
