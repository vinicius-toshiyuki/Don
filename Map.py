from random import choice, randint as rand
import copy

class Map:
    def __init__(s, name, encounter_rate, connections, units):
        s._name = name
        s._encounter_rate = int(encounter_rate)
        s._connections = connections
        s._units = units

        s._din_encounter_rate = s._encounter_rate

    def get_creature(s, name=None):
        try:
            if name is None:
                name = choice(list(s._units["creature"].keys()))
            return copy.copy(s._units["creature"][name])
        except:
            return None

    def get_encounter(s):
        if rand(0, 99) <= s._din_encounter_rate:
            if (c := s.get_creature()) is not None:
                s._din_encounter_rate = s._encounter_rate
                return c
        else:
            s._din_encounter_rate += s._din_encounter_rate * 0.05
        return None

    def get_connections(s):
        return s._connections

    def __str__(s):
        return s._name
