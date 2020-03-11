import unittest
import Unit
import Inventory

class TestUnit(unittest.TestCase):
    def setUp(s):
        Inventory.Inventory.set(None)

    def test_player_creation(s):
        with s.assertRaises(ValueError):
            p = Unit.Player('Nome', Inventory.Inventory(), 0, -1, -3, -4, -5, 6, 7, 8)
        with s.assertRaises(ValueError):
            p = Unit.Player('Nome', Inventory.Inventory(), 1, 2, 3, 4, 5, 0, 7, -8)
        with s.assertRaises(ValueError):
            p = Unit.Player('Nome', Inventory.Inventory(), 1, 2, 3, 4, 5, 6, 8, 8)
        p = Unit.Player('Nome', Inventory.Inventory(), 1, 2, 3, 4, 5, 6, 7, 8)

        s.assertEqual(p.name, 'Nome')
        s.assertEqual(p.max_health, 1)
        # health tem que ser no máximo max_health
        s.assertEqual(p.health, 1)
        s.assertEqual(p.attack, 3)
        s.assertEqual(p.defense, 4)
        s.assertEqual(p.agility, 5)
        s.assertEqual(p.level, 6)
        s.assertEqual(p.exp, 7)
        s.assertEqual(p.exp_to_next, 8)

        s.assertFalse(p.max_health <= 0)
        s.assertFalse(p.health <= 0)
        s.assertFalse(p.attack <= 0)
        s.assertFalse(p.defense <= 0)
        s.assertFalse(p.agility <= 0)
        s.assertFalse(p.level <= 0)
        s.assertFalse(p.exp < 0)
        s.assertFalse(p.exp_to_next <= 0)

    def test_player_methods(s):
        p = Unit.Player('Nome', Inventory.Inventory(), 3, 1, 1, 4, 5, 6, 7, 8)
        s.assertEqual(p.health, 1)
        p.heal(1)
        s.assertEqual(p.health, 2)
        p.heal(10)
        s.assertEqual(p.health, p.max_health)
        with s.assertRaises(ValueError):
            p.heal(-45)

if __name__ == '__main__':
    unittest.main()
