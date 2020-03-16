from Unit import Player
from random import choice, randint as rand
import termwin as tw
import Prompt as pmt
from termwin.frame import Frame
from termwin.window import Window
from termwin.loopwindow import LoopWindow

class Game:
	def __init__(s, units, maps, items):
		s._units = units
		s._maps = maps
		s._items = items

		s._wm = tw.Manager()

		f1 = Frame(weight=3, orientation='horizontal') # f2 e status
		f2 = Frame() # mochila e main
		s.w0 = LoopWindow(timeout=3, background='222222') # mochila
		s.w1 = Window(timeout=.3, background='222222') # main
		f2.addwidget(s.w1)
		f2.addwidget(s.w0)
		s.w2 = LoopWindow(timeout=4, background='222222') # status
		f1.addwidget(f2)
		f1.addwidget(s.w2)

		f3 = Frame(orientation='horizontal')
		s.w3 = LoopWindow(timeout=3, background='222222')
		s.w4 = LoopWindow(timeout=3, background='222222')
		f3.addwidget(s.w3)
		f3.addwidget(s.w4)

		s._wm.root.addwidget(f1)
		s._wm.root.addwidget(f3)

		pmt.wprompt = s.w3
		pmt.winput = s.w4

		s._player = units["player"]
		s.__map = maps['Home']

	def mainloop(s):
		tw.setraw()

		while True:
			if (c := s.__map.get_encounter()) is not None:
				s.w1.wipe()
				s.w1.print('{} encountered {}'.format(s._player, c))
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
							s.w1.print('{} received an item'.format(s._player))
							s._player.inventory.put(c.inventory.take(i, drop_count))

					exp = c.exp_value()
					s.w1.print("{} received {} experience".format(s._player, exp))
					if (att_change := s._player.grant_exp(exp)):
						s.w2.wipe()
						s.w2.print("Level up!")
						for stat in s._player.stats:
							s.w2.print("{}: {}".format(stat, s._player.stats[stat]) + (" (+{})".format(att_change[stat]) if stat in att_change else ''))
				elif s._player.health <= 0:
					s.w1.print("Game Over")
					break

			if s._action():
				break
		tw.unsetraw()
		s._wm.die()
		
	def _action(s):
		s.__show_stats(s._player)
		s.__show_items(s._player)
		if (i := pmt.prompt(
			"Take an action:",
			("Wait", "Walk", 'Bag', 'Quit'), #, "Stats", "Bag"),
			pmt.default)) == "Wait":
			s.w1.wipe()
			s.w1.print("{} waited".format(s._player))
		elif i == "Walk":
			s.__walk()
		#elif i == "Stats":
		#	s.__show_stats(s._player)
		#	s._action()
		elif i == "Bag":
			s.__item_menu(s._player)
			s._action()
		elif i == 'Quit':
			s.w1.print('You are weak!')
			return True
		return False

	def _change_map(s, connection):
		s.__map = s._maps[connection]

	def _battle(s, u1, u2, turn=1):
		def __fight(u1, u2):
			if turn == int(turn):
				s.w1.wipe()
			s.w1.print('[{}] '.format(int(turn)) + "{} took {} damage from {}".format(u2, u2.take_damage(u1.get_damage()), u1))
		def __guard(u):
			if turn == int(turn):
				s.w1.wipe()
			s.w1.print('[{}] '.format(int(turn)) + "{} is on guard!".format(u))
			u.guard()
		def __run(u1, u2):
			if turn == int(turn):
				s.w1.wipe()
			if u1.run(u2):
				s.w1.print('[{}] '.format(int(turn)) + "{} ran away from combat".format(u1))
				return True
			else:
				s.w1.print('[{}] '.format(int(turn)) + "{} tried to run away but failed!".format(u1))
				return False

		if not u1.health > 0:
			s.w1.print("{} won".format(u2))
			return u2
		if not u2.health > 0:
			s.w1.print("{} won".format(u1))
			return u1

		u1.unguard()

		if type(u1) == Player:
			s.__show_stats(u1)
			# TODO: Isso aqui não dá certo para pular linha -> s.w2.print()
			# Nem \n no começo da string
			s.w2.print(' ')
			s.w2.print("{} has {}/{} health".format(u1, u1.health, u1.max_health))
			s.w2.print("{} has {}/{} health".format(u2, u2.health, u2.max_health))
			action = pmt.prompt(
					"Choose an action:",
					("Fight", "Guard", "Show items", "Run"), #, "Show stats"),
					pmt.default)
		else:
			action = choice(["Fight"] * 2 + ["Guard"])

		if action == "Fight":
			__fight(u1, u2)
		elif action == "Guard":
			__guard(u1)
		elif action == "Show items":
			if s.__item_menu(u1) is None:
				u1, u2 = u2, u1
		elif action == "Run":
			if __run(u1, u2):
				return u2
		#elif action == "Show stats":
		#	s.__show_stats(u1)
		#	u1, u2 = u2, u1
		
		return s._battle(u2, u1, turn+0.5)
		
	def __show_stats(s, u):
		s.w2.wipe()
		s.w2.print('\n'.join([
			'{}: {}'.format(stat, u.stats[stat]) for stat in u.stats]))

	def __show_items(s, u):
		s.w0.wipe()
		s.w0.print('Items:')
		s.w0.print('\n'.join([
			'{} ({})'.format(i, u.inventory.count(i)) for i in u.inventory.items]))

	def __item_menu(s, u):
		i = pmt.prompt(
				"Items:",
				[pmt.go_back] + ["{} ({})".format(i, u.inventory.count(i)) for i in u.inventory.items],
				pmt.default,
				return_option=True
				)
		if i != pmt.default:
			item = u.inventory.take(u.inventory.items[i-2])
			if item.consumable and pmt.prompt(
					"Consume {}".format(item),
					("Yes", "No"),
					pmt.default
					) == "Yes":
				s.w1.print("{} consumed {}".format(s._player, item))
				u.use_item(item)
				return str(item)
			else:
				u.inventory.put(item)
				return s.__item_menu(u)
		return None

	def __walk(s):
		if (i := pmt.prompt(
				"Where to go:",
				[pmt.go_back] + s.__map.connections,
				pmt.default
				)) != pmt.go_back:
			s.w1.print("{} walked to {}".format(s._player, i))
			s._change_map(i)
