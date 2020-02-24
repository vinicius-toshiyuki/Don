from IO import *
from Log import *
from Unit import Player
from random import choice

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
                winner = s._battle(
                       *sorted(
                            (s._player, c,),
                            key=lambda u: u.get_stats()["Agility"]
                            )) 
                if winner == s._player and (att_change := s._player.grant_exp(c.exp_value())):
                    Log.put("Level up!", Game.__player_tag)
                    for stat in s._player.get_stats():
                        Log.put("{}: {}".format(stat, s._player.get_stats()[stat]) + (" (+{})".format(att_change[stat]) if stat in att_change else ''), s.__player_tag)
                if winner == c:
                    Log.put("Game Over", "Game")
                    Log.flush()
                    exit()

            s._action()
        
    def _action(s):
        if (i := IO.prompt(
            "Take an action:",
            ("Wait", "Walk", "Stats", "Bag"),
            IO.default)) == "Wait":
                pass
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
        if not u1.is_alive():
            Log.put("{} won".format(u2), Game.__battle_tag)
            return u2
        if not u2.is_alive():
            Log.put("{} won".format(u1), Game.__battle_tag)
            return u1

        u1.unguard()
        Log.put("{} has {}/{} health".format(u1, *u1.get_stats()["Health"]), Game.__battle_tag)
        Log.put("{} has {}/{} health".format(u2, *u2.get_stats()["Health"]), Game.__battle_tag)

        if type(u1) == Player:
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
            s.__run(u1, u2)
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
        Log.put("Run not working", "TODO")

    def __show_stats(s, u):
        [Log.put(
            "{}: {}".format(stat, u.get_stats()[stat]),
            Game.__player_tag
            ) for stat in u.get_stats()]

    def __item_menu(s, u):
        i = IO.prompt(
                "Items:",
                [IO.go_back] + ["{} ({})".format(i, i.count()) for i in u.get_items()],
                IO.default,
                return_option=True
                )
        if i != IO.default:
            item = u.get_items()[i - 2]
            if item.is_consumable() and IO.prompt(
                    "Consume {}".format(item),
                    ("Yes", "No"),
                    IO.default
                    ) == "Yes":
                Log.put("{} consumed {}".format(s._player, item), s.__player_tag)
                item.consume(u)
                return str(item)
            else:
                return s.__item_menu(u)
        return None

    def __walk(s):
        if (i := IO.prompt(
                "Where to go:",
                [IO.go_back] + s.__map.get_connections(),
                IO.default
                )) != IO.go_back:
            s._change_map(i)
            
"""
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
    return fight(u2, u1)"""
