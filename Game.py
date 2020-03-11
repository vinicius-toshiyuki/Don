from IO import *
from Log import *
from Unit import Player
from random import choice, randint as rand

class Game:
    __battle_tag = "Battle"
    __player_tag = "Player"

    def __init__(s, units, maps, items):
        s._units = units
        s._maps = maps
        s._items = items

        s._player = units["player"]
        s.__map = maps['Home']

    def mainloop(s):
        while True:
            if (c := s.__map.get_encounter()) is not None:
                Log.put("{} encountered {}".format(s._player, c), s.__battle_tag)
                winner = s._battle(
                       *sorted(
                            (s._player, c,),
                            key=lambda u: u.agility
                            )) 
                if winner == s._player:
                    for i in c.inventory.items:
                        drop_rate = c.drop_rates[i]
                        item_count = c.inventory.count(i)
                        drop_count = 0
                        while drop_count < item_count and rand(0,99) < drop_rate:
                            drop_count += 1
                            drop_rate /= 2

                        if drop_count > 0:
                            Log.put('{} received an item'.format(s._player), s.__player_tag)
                            s._player.inventory.put(c.inventory.take(i, drop_count))

                    exp = c.exp_value()
                    Log.put("{} received {} experience".format(s._player, exp), s.__player_tag)
                    if (att_change := s._player.grant_exp(exp)):
                        Log.put("Level up!", Game.__player_tag)
                        for stat in s._player.stats:
                            Log.put("{}: {}".format(stat, s._player.stats[stat]) + (" (+{})".format(att_change[stat]) if stat in att_change else ''), s.__player_tag)
                else:
                    Log.put("Game Over", "Game")
                    Log.flush()
                    exit()

            s._action()
        
    def _action(s):
        if (i := IO.prompt(
            "Take an action:",
            ("Wait", "Walk", "Stats", "Bag"),
            IO.default)) == "Wait":
            Log.put("{} waited".format(s._player), s.__player_tag)
        elif i == "Walk":
            s.__walk()
        elif i == "Stats":
            s.__show_stats(s._player)
            s._action()
        elif i == "Bag":
            s.__item_menu(s._player)
            s._action()

    def _change_map(s, connection):
        s.__map = s._maps[connection]

    def _battle(s, u1, u2):
        if not u1.health > 0:
            Log.put("{} won".format(u2), Game.__battle_tag)
            return u2
        if not u2.health > 0:
            Log.put("{} won".format(u1), Game.__battle_tag)
            return u1

        u1.unguard()

        if type(u1) == Player:
            Log.put("{} has {}/{} health".format(u1, u1.health, u1.max_health), Game.__battle_tag)
            Log.put("{} has {}/{} health".format(u2, u2.health, u2.max_health), Game.__battle_tag)
            action = IO.prompt(
                    "Choose an action:",
                    ("Fight", "Guard", "Show items", "Run", "Show stats"),
                    IO.default)
        else:
            action = choice(["Fight"] * 2 + ["Guard"])
        
        if action == "Fight":
            s.__fight(u1, u2)
        elif action == "Guard":
            s.__guard(u1)
        elif action == "Show items":
            if s.__item_menu(u1) is None:
                u1, u2 = u2, u1
        elif action == "Run":
            if s.__run(u1, u2):
                return u2
        elif action == "Show stats":
            s.__show_stats(u1)
            u1, u2 = u2, u1
        
        return s._battle(u2, u1)
        
    def __fight(s, u1, u2):
        Log.put("{} took {} damage from {}".format(u2, u2.take_damage(u1.get_damage()), u1), Game.__battle_tag)

    def __guard(s, u):
        Log.put("{} is on guard!".format(u), Game.__battle_tag)
        u.guard()

    def __run(s, u1, u2):
        if u1.run(u2):
            Log.put("{} ran away from combat".format(u1), s.__battle_tag)
            return True
        else:
            Log.put("{} tried to run away but failed!".format(u1), s.__battle_tag)
            return False

    def __show_stats(s, u):
        [Log.put(
            "{}: {}".format(stat, u.stats[stat]),
            Game.__player_tag
            ) for stat in u.stats]

    def __item_menu(s, u):
        i = IO.prompt(
                "Items:",
                [IO.go_back] + ["{} ({})".format(i, u.inventory.count(i)) for i in u.inventory.items],
                IO.default,
                return_option=True
                )
        if i != IO.default:
            item = u.inventory.take(u.inventory.items[i-2])
            if item.consumable and IO.prompt(
                    "Consume {}".format(item),
                    ("Yes", "No"),
                    IO.default
                    ) == "Yes":
                Log.put("{} consumed {}".format(s._player, item), s.__player_tag)
                u.use_item(item)
                return str(item)
            else:
                u.inventory.put(item)
                return s.__item_menu(u)
        return None

    def __walk(s):
        if (i := IO.prompt(
                "Where to go:",
                [IO.go_back] + s.__map.connections,
                IO.default
                )) != IO.go_back:
            Log.put("{} walked to {}".format(s._player, i), s.__player_tag)
            s._change_map(i)
