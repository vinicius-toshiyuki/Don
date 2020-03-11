import fcntl
from math import ceil
import struct
import termios
import sys
from random import randint as rand
from threading import Thread
from time import sleep

s = struct.pack('HHHH', 0, 0, 0, 0)
x = fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, s)
h, w = struct.unpack('HHHH', x)[:2]

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

class Window:
	def __init__(s, refresh_time=3):
		def refresh(s):
			while True:
				s._ready = True
				if len(s._old_content) > 0:
					s._content.insert(0, s._old_content[-1])
				s._old_content = []
				sleep(s._time)
		s._ready = True
		s._time = refresh_time
		s.__refresher = Thread(target=refresh, args=(s,))

		s._content = []
		s._old_content = []
		
		s._background = tuple(rand(0,255) for _ in range(3))

		s.__refresher.start()

	def put(s, content):
		s._content += str(content).splitlines()

	def draw(s, column, row, height, width):
		move(column, row)
		print('\033[48;2;{};{};{}m'.format(*s._background), end='')
		for _ in range(height):
			if s._ready:
				text = s._content.pop(0) if len(s._content) > 0 else ' '*width
				s._old_content.append(text)
				text = s._old_content[-1][:width].ljust(width)
			else:
				text = s._old_content[_][:width].ljust(width)
			print(text, end='')
			left(width)
			down(1)
		print('\033[0m', end='')
		# TODO: corrida
		s._ready = False

class Frame:
	def __init__(s, orientation):
		s._orientation = orientation
		s.areas = []

	@property
	def orientation(s): return s._orientation

	def addWindow(s):
		#if (len(s.areas) * 2 + 1) >= s._height:
		#	raise Exception('can\'t use that many windows')
		s.areas.append(Window())
		return s.areas[-1]

	def addFrame(s, orientation):
		s.areas.append(Frame(orientation))
		return s.areas[-1]

	def draw(s, column, row, height, width):
		if s.orientation == 'vertical':
			aheight = height // len(s.areas) - 1 if len(s.areas) > 0 else 0
			awidth = width
		elif s.orientation == 'horizontal':
			aheight = height
			awidth = width // len(s.areas) - 1 if len(s.areas) > 0 else 0

		print('\033[{};{}H'.format(column, row), end='')
		roffset = 0
		coffset = 0
		for a in s.areas:
			a.draw(column + coffset, row + roffset, aheight, awidth)

			if s._orientation == 'vertical':
				roffset += aheight + 1
				if a != s.areas[-1]:
					print('-' * awidth, end='')
			elif s._orientation == 'horizontal':
				coffset += awidth + 1
				if a != s.areas[-1]:
					pass
			print(flush=True, end='')

class Root(Frame):
	def __init__(s, column, row, height, width, orientation):
		super().__init__(orientation)
		s._column = column
		s._row = row
		s._height = height
		s._width = width

	def draw(s):
		super().draw(s._column, s._row, s._height, s._width)

class Manager:
	def __init__(s, height, width):
		s.root = Root(1, 1, height, width, 'vertical')
		w1 = s.root.addWindow()
		w1.put('oie gente')
		w1.put('estou testando meu buffer')
		w1.put('com um texto beeeeem loooongo para ber se ele cooooorta mesmo onde deveria')
		w1.put('e se nao mostra quando nao tem linha')
		w1.put('e se nao mostra quando nao tem linha')
		w1.put('e se nao mostra quando nao tem linha')
		w1.put('e se nao mostra quando nao tem linha')
		w1.put('agira eu quero ver')
		w1.put('eu quero ver')
		w1.put('sera que dunciona')
		f1 = s.root.addFrame('horizontal')
		w4 = f1.addWindow()
		w4.put('e mostra no buffer certo')
		w5 = f1.addWindow()
		f2 = f1.addFrame('vertical')
		w6 = f2.addWindow()
		w7 = f2.addWindow()
	def draw(s):
		print('\033[2J', end='')
		s.root.draw()

	def mainloop(s):
		while True:
			s.draw()
			sleep(1/2)

m = Manager(h, w)
m.mainloop()
