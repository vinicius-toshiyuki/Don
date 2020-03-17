import curses
from curses.textpad import *

class window:
	_ididx = 0
	def __init__(s, weight=1):
		try: # verifica se já tem id
			s._id
		except: # se não tem coloca como -1
			s._id = -1
		finally: # se já foi iniciada erro
			if s._id >= 0:
				raise Exception('Can not init this window again')

		s.weight = weight

		s._id = window._ididx
		window._ididx += 1
		s._w = curses.newwin(0, 0)

	@property
	def id(s): return s._id

	def refresh(s):
		s._w.refresh()
	def resize(s, *args):
		s._w.resize(*args)
	def mvwin(s, *args):
		s._w.mvwin(*args)
	def addstr(s, *args):
		s._w.addstr(*args)

class frame:
	def __init__(s, line, col, height, width, orientation='vertical'):
		s._wins = {}
		s._hidden = {}
		s._line = line
		s._col = col
		s._height = height
		s._width = width
		s._orientation = orientation

	@property
	def line(s): return s._line
	@property
	def col(s): return s._col
	@property
	def height(s): return s._height
	@property
	def width(s): return s._width
	@property
	def orientation(s): return s._orientation

	def addwin(s, win):
		s._wins[win.id] = win
		s.refresh()
	def remwin(s, win):
		if win.id in s._wins:
			s._wins.pop(win.id)
			s.refresh()
		elif win.id in s._hidden:
			s._hidden.pop(win.id)
		else:
			raise Exception('Window not in frame')
	def hidewin(s, win):
		if win.id in s._wins:
			s._hidden[win.id] = s.window.pop(win.id)
			s.refresh()
		else:
			raise Exception('Window not in frame windows')
	def unhidewin(s, id):
		if win.id in s._hidden:
			s._wins[win.id] = s._hidden.pop(win.id)
			s.refresh()
		else:
			raise Exception('Window not in frame hidden windows')
	def refresh(s):
		tweight = sum([s._wins[w].weight for w in s._wins])
		sep = max(len(s._wins) - 1, 0)
		if tweight > 0:
			wheight = (s.height - sep) // tweight if s.orientation == 'vertical' else s.height
			wwidth = (s.width - sep) // tweight if s.orientation == 'horizontal' else s.width

			yoff, xoff = s.line, s.col
			for w in s._wins:
				w = s._wins[w]
				w.resize(
						wheight * (w.weight if s.orientation == 'vertical' else 1),
						wwidth * (w.weight if s.orientation == 'horizontal' else 1)
						)
				w.mvwin(1, 1) #yoff, xoff)
				yoff += wheight * (w.weight if s.orientation == 'vertical' else 0)
				xoff += wwidth * (w.weight if s.orientation == 'horizontal' else 0)
				w.refresh()

def main(stdscr):
	#stdscr.addstr('{}×{}'.format(curses.LINES, curses.COLS))
	#curses.start_color()

	w1 = curses.newwin(5, 10, 1, 1)
	w2 = curses.newwin(5, 10, 1, 13)
	w1.refresh()
	w2.refresh()
	#f = frame(1, 1, curses.LINES - 1, curses.COLS - 1)
	#w1 = window(2)
	#w2 = window()
	#f.addwin(w1)
	#f.addwin(w2)

	#w1.addstr(0, 0, 'texto 1')
	#w1.refresh()
	#w2.addstr(0, 0, 'texto 2')
	#w2.refresh()

	w1.overlay(stdscr)
	w2.overlay(stdscr)

	rectangle(stdscr, 0,0,6,11)
	rectangle(stdscr, 0,12,6,23)
	stdscr.refresh()
	b = Textbox(w1)
	w1.scrollok(True)
	m = b.edit()
	stdscr.getch()
	w1.getch()
curses.wrapper(main)
