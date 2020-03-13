import time
import fcntl
import struct
import termios
import sys
import os
import tty
import Widget.Manager as wm

class IO:
	__old = None
	__flags = None
	def setraw():
		IO.__old = termios.tcgetattr(sys.stdin)
		new = termios.tcgetattr(sys.stdin)

		new[3] &= ~termios.ECHO
		new[3] &= ~termios.ICANON

		termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, new)

		IO.__flags = fcntl.fcntl(sys.stdin, fcntl.F_GETFL) 
		fcntl.fcntl(sys.stdin, fcntl.F_SETFL, IO.__flags | os.O_NONBLOCK) 

	def unsetraw():
		IO.__old[3] |= termios.ECHO
		IO.__old[3] |= termios.ICANON
		termios.tcsetattr(sys.stdin, termios.TCSANOW, IO.__old)
		fcntl.fcntl(sys.stdin, fcntl.F_SETFL, IO.__flags)

	def read(stop=13, tab=4):
		s = ''
		while (c := int.from_bytes(sys.stdin.buffer.read(1), 'big')) != stop:
			if c == 0o10:
				s = s[:len(s)]
			elif c == 0o11:
				s += ' '*tab
			else:
				s += chr(c)
			time.sleep(.1)
		return s

	def readshow(window):
		ret = ''
		window.put(' ')
		while (c := IO.readchar()) != '\n':
			ret += c
			window.modify(lambda x: x + c if x != ' ' else c)
		return ret

	def readchar():
		get = lambda: sys.stdin.buffer.raw.read(1)
		while not (c := get()):
			time.sleep(1/24)
		while True:
			try:
				c = c.decode()
				if c == '[' and get().decode() == 'C':
					c = '>'
				break
			except:
				c += get()

		return c

	def gettermsize():
		st = struct.pack('HHHH', 0, 0, 0, 0)
		x = fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, st)
		height, width = struct.unpack('HHHH', x)[:2]
		return (height, width)

	def prompt(window, title, options, default=None, valid=None, indexes=True):
		if type(options) != dict:
			options = dict(enumerate(options, 1))

		IO.log(window, '{}'.format(title))
		for o in options:
			IO.log(window, '[{}] {}'.format(o, options[o]))

		o = IO._input(window, 'Option:', options.keys() if valid is None else valid, default)
		return o if indexes else options[o]

	def _input(window, text=None, options=None, default=None):
		if text is not None:
			if default is not None:
				text += '[{}]'.format(default)
			text += ' '
			IO.log(window, text)

		if options is None:
			while (i := IO.read()) == '':
				if default is not None:
					i = default
					break
			return i
		else:
			while (i := IO.read()) not in [str(o) for o in options]:
				if i == '' and default in options:
					i = default
					break
				IO.log(window, 'Invalid option!')
			return type(list(options)[0])(i)

	def log(window, text):
		window.put(text)
