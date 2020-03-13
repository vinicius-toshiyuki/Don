import fcntl
import re
from math import ceil
import struct
import termios
import sys
from random import randint as rand
from threading import Thread, Condition
from time import sleep

def up(count):
	print('\033[{}A'.format(count), end='')
def down(count):
	print('\033[{}B'.format(count), end='')
def right(count):
	print('\033[{}C'.format(count), end='')
def left(count):
	print('\033[{}D'.format(count), end='')

def move(column, row):
	print('\033[{};{}H'.format(row, column), end='')

def gettermsize():
	st = struct.pack('HHHH', 0, 0, 0, 0)
	x = fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, st)
	height, width = struct.unpack('HHHH', x)[:2]
	return height, width

class Widget:
	def __init__(s, weight=1, background='000000', foreground='ffffff'):
		s._column = 0
		s._row = 0
		s._height = 0
		s._width = 0
		s._weight = weight

		s._die = False
		s._new = True
		s.parent = None
		s._background = tuple(int(background[i:i+2], 16) for i in (0,2,4))
		s._foreground = tuple(int(foreground[i:i+2], 16) for i in (0,2,4))

		s._clean()

	def die(s):
		s._die = True

	@property
	def weight(s): return s._weight
	@property
	def height(s): return s._height
	@property
	def width(s): return s._width
	@property
	def column(s): return s._column
	@property
	def row(s): return s._row

	def _clean(s):
		move(s._column, s._row)
		s._setbackground()
		print(''.join([' ' * s._width + '\033[{}D\033[1B'.format(s._width)] * s._height), end='')
		s._setdown()
	def _setup(s):
		if s._new:
			s._new = False
			s._clean()
		move(s._column, s._row)
		s._setbackground()
		s._setforeground()
	def _setdown(s):
		s._resetcolors()
		move(s._column, s._row + s._height)
	def _setbackground(s):
		print('\033[48;2;{};{};{}m'.format(*s._background), end='')
	def _setforeground(s):
		print('\033[38;2;{};{};{}m'.format(*s._foreground), end='')
	def _setcolors(s):
		s._setbackground()
		s._setforeground()
	def _resetcolors(s):
		print('\033[0m', end='')

	def _draw(s): s._clean()

	def resize(s, column, row, height, width):
		s._column = column
		s._row = row
		s._height = height
		s._width = width
		s._new = True
		s._clean()

class Window(Widget):
	def _clean(s):
		_, maxwidth = gettermsize()
		s._setbackground()
		s._setforeground()
		move(s._column, s._row)
		s.__off = 0
		print(''.join([' ' * s._width + '\033[{}D\033[1B'.format(s._width if maxwidth > s.column + s.width else (s._width - 1))] * s._height), end='')
		#print(''.join([''.join([str(i%10) for i in range(s._width)]) + '\033[{}D\033[1B'.format(s._width if maxwidth > s.column + s.width else (s._width - 1))] * s._height), end='')
		s._setdown()

	def __init__(s, weight=1, background='000000', foreground='ffffff', timeout=0, maxlines=100):
		super().__init__(weight, background, foreground)

		s._ready = True
		s._timeout = timeout
		s.__idx = 0
		s.__off = 0

		s._content = []
		s._max = maxlines

		s.__refresh_cond = Condition()
		s.__refresher = Thread(target=s._refresh)
		s.__refresher.start()

		s.__draw_cond = Condition()
		s.__drawer = Thread(target=s._draw)
		s.__drawer.start()

		s._clean()

	def die(s):
		s._die = True
		s.__refresh_cond.acquire()
		s.__draw_cond.acquire()

		s.__refresh_cond.notify_all()
		s.__draw_cond.notify_all()

		s.__refresh_cond.release()
		s.__draw_cond.release()

		s.__refresher.join()
		s.__drawer.join()

	def _refresh(s):
		while not s._die:
			s.__refresh_cond.acquire()
			s.__refresh_cond.wait()
			s._ready = False
			s.__refresh_cond.release()
			sleep(s._timeout)
			s.__refresh_cond.acquire()
			s.__off = 0
			s._new = True
			s._ready = True
			s.__refresh_cond.release()
			s.__draw_cond.acquire()
			s.__draw_cond.notify()
			s.__draw_cond.release()

	def resize(s, column, row, height, width):
		super().resize(column, row, height, width)
		s.__idx = s.__idx - s.__off
		s.__off = 0

		s._clean()

	def _parsetext(s, text):
		text = text.replace('\t', ' ' * 4)
		return tuple(text[i:i+s._width] + '\033[{}D\033[1B'.format(s._width) for i in range(0, len(text), s._width))

	def put(s, content):
		s.__draw_cond.acquire()
		s._content += str(content).splitlines()
		s.__idx -= len(s._content[s._max:])
		s._content = s._content[-s._max:]
		s.__draw_cond.notify()
		s.__draw_cond.release()

	def modify(s, modifier):
		mod = modifier(s._content.pop(-1)).splitlines()
		for i, line in enumerate(mod):
			while '\b' in line:
				mod[i] = re.sub('[^\b]\b', '', line)
		s.__idx -= len(mod)
		s.__off = max(s.__off - 1, 0)
		s.put('\n'.join(mod))

	def __str__(s):
		return 'idx: {} off: {} height: {} len: {} {}'.format(s.__idx, s.__off, s._height, len(s._content), len(s._parsetext(s._content[-1] if len(s._content) > 0 else 'a')))

	def _draw(s):
		while not s._die:
			s.__draw_cond.acquire()
			s.__draw_cond.wait()
			s._setup()
			move(s._column, s._row + s.__off)
			for i in range(s.__idx, len(s._content)):
				text = s._parsetext(s._content[i])
				if len(text) < s._height - s.__off + 1:
					print(''.join(text), end='', flush=True)
					s.__idx += 1
					s.__off += 1
				else:
					s.__refresh_cond.acquire()
					s.__refresh_cond.notify()
					s.__refresh_cond.release()
					break
			s._setdown()
			s.__draw_cond.release()

class Frame(Widget):
	def __init__(s, weight=1, background='000000', foreground='ffffff', orientation='vertical'):
		super().__init__(weight, background, foreground)

		s._orientation = orientation
		s.__widgets = []
		s._clean()

	def die(s):
		for w in s.__widgets:
			w.die()
		s._die = True

	def resize(s, column, row, height, width):
		s._column = column
		s._row = row
		s._height = height
		s._width = width

		weight = sum([w.weight for w in s.__widgets]) # peso total de todos os widgets
		if weight == 0:
			wheight = s._height
			wwidth = s._width
		elif s.orientation == 'vertical':
			wheight = (s._height - len(s.__widgets) + 1) // weight # altura de cada peso de widget
			wwidth = s._width
			spare = (s._height - len(s.__widgets) + 1) % weight
		elif s.orientation == 'horizontal':
			wheight = s._height
			wwidth = (s._width - len(s.__widgets) + 1) // weight # largura de cada peso de widget
			spare = (s._width - len(s.__widgets) + 1)  % weight

		s._clean()
		roffset, coffset = 0, 0
		for w in s.__widgets:
			w.resize(
					s._column + coffset,
					s._row + roffset,
					wheight * (w.weight if s.orientation == 'vertical' else 1) + (1 if spare > 0 and s.orientation == 'vertical' else 0),
					wwidth * (w.weight if s.orientation == 'horizontal' else 1) + (1 if spare > 0 and s.orientation == 'horizontal' and w != s.__widgets[-1] else 0)
					)
			if s._orientation == 'vertical':
				roffset += wheight * w.weight + (2 if spare > 0 else 1)
			elif s._orientation == 'horizontal':
				coffset += wwidth * w.weight + (2 if spare > 0 and w != s.__widgets[-1] else 1)
			spare -= 1
		s._draw()

	@property
	def orientation(s): return s._orientation

	def addwidget(s, widget):
		s.__widgets.append(widget)
		widget.parent = s
		s.resize(s._column, s._row, s._height, s._width)

	def _draw(s):
		s._setup()
		for w in s.__widgets:
			if s.orientation == 'vertical' and w != s.__widgets[-1]:
				move(w.column, w.row + w.height)
				print('─' * s._width, end='')
			elif s.orientation == 'horizontal' and w != s.__widgets[-1]:
				move(w.column + w.width, w.row)
				print('│\033[1D\033[1B' * s._height, end='')
		print(flush=True, end='')
		s._setdown()

class Root(Frame):
	def __init__(s, column, row, height, width, orientation='vertical'):
		super().__init__(orientation=orientation)
		s._column = column
		s._row = row
		s._height = height
		s._width = width

class Manager:
	def __init__(s):
		height, width = gettermsize()
		height = 25
		width = 50

		s._root = Root(1, 1, height, width, orientation='vertical')
		s._new = True
		s._die = False

		s.__mainlooper = Thread(target=s.mainloop)

	def die(s):
		s._root.die()
		s._die = True
		s.__mainlooper.join()

	@property
	def root(s): return s._root

	def draw(s):
		if s._new:
			s._new = False
			print('\033[2J', end='')
		s._root.draw()

	def mainloop(s):
		while not s._die:
			#s.draw()
			sleep(1/2)

	def background(s):
		s.__mainlooper.start()

# m = Manager()
# 
# w1 = Window(weight=2, timeout=3, background='ff0000')
# w1.put('alooo')
# w1.put('mais um testo')
# 
# w2 = Window(weight=3, timeout=10, background='00aa22')
# w2.put('ttes:')
# 
# f1 = Frame(orientation='horizontal', background='223344')
# w3 = Window(timeout=10, background='aa0066')
# w4 = Window(timeout=10, background='aa0066')
# w5 = Window(weight=2, timeout=10, background='aa0066')
# f1.addwidget(w3)
# f1.addwidget(w4)
# f1.addwidget(w5)
# 
# m.root.addwidget(w1)
# m.root.addwidget(w2)
# m.root.addwidget(f1)
# 
# m.background()
# sleep(2)
# 
# w1.put('1 depois de um tempo')
# w1.put('2 depois de um tempo')
# w1.put('3 depois de um tempo')
# w1.put('4 depois de um tempo')
# w1.put('5 depois de um tempo')
# w1.put('6 depois de um tempo')
# w1.put('7 depois de um tempo')
# w1.put('7.5 depois de um tempo')
# w1.put('um texto beeeewm looongo meseeesweamooo pata tesstaaaaar')
# w1.put('8 depois \tde \tum \t\t\t\ttempo')
# w1.put('9 depois de um tempo')
# w1.put('10 depois de um tempo')
# w1.put('11 depois de um tempo')
# w1.put('12 depois de um tempo')
# w1.modify(lambda x: 'mudado\ne mais')
# w1.put('um texto beeeewm looongo meseeesweamooo pata tesstaaaaar')
# 
# w5.put('{}x{} {}x{}'.format(w5.height, w5.width, w5.column, w5.row))
# w4.put('{}x{} {}x{}'.format(w4.height, w4.width, w4.column, w4.row))
# w3.put('{}x{} {}x{}'.format(w3.height, w3.width, w3.column, w3.row))
# w2.put('{}x{} {}x{}'.format(w2.height, w2.width, w2.column, w2.row))
# w1.put('{}x{} {}x{}'.format(w1.height, w1.width, w1.column, w1.row))
# 
# w3.put('3 agora')
# w4.put('4 agora')
# w5.put('5 agora')
