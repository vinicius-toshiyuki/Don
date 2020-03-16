import termwin as tw
from time import sleep
from curses import wrapper
from pynput.keyboard import Key, Listener

def main(stdscr):
	bounds = (1,1,20,20)
	row = bounds[0]
	col = bounds[1]
	print('\x1b[2J\x1b[{};{}H'.format(*bounds[:2]), end='', flush=True)

	k = []
	def on_press(key):
		if key not in k:
			k.append(key)
	def on_release(key):
		if key == Key.esc:
			return False
		if key in k:
			k.pop(k.index(key))

	with Listener(on_press=on_press, on_release=on_release) as listener:
		tw.setraw()
		while Key.esc not in k:
			print(tw._move(int(col), int(row)), end='', flush=True)
			print(' ', end='', flush=True)
			if Key.up in k and row > bounds[0]:
				row -= .4
			if Key.down in k and row < bounds[2]:
				row += .4
			if Key.right in k and col < bounds[3]:
				col += .4
			if Key.left in k and col > bounds[1]:
				col -= .4
			print(tw._move(int(col), int(row)), end='', flush=True)
			print('0', end='', flush=True)
			sleep(1/60)
		tw.unsetraw()

wrapper(main)
