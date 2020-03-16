import curses
from curses.textpad import Textbox, rectangle

def main(stdscr):
	stdscr.keypad(True)
	# height width row column
	w1 = curses.newwin(5, 30, 1, 1)
	w2 = curses.newwin(5, 30, 1, 32)
	w1.border()
	w2.border()
	#rectangle(stdscr, 0, 0, 7, 32)
	#rectangle(stdscr, 0, 33, 7, 63)
	stdscr.refresh()

	box = Textbox(w1)
	box = Textbox(w2)

	box.edit()

	message = box.gather()
	stdscr.keypad(False)
	print(message)

curses.wrapper(main)
