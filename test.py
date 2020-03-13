import Widget.Manager as wm
from IO.Input import *

m = wm.Manager()
w1 = wm.Window(weight=1, background='223322')
w2 = wm.Window(background='443344')
f1 = wm.Frame(orientation='horizontal', background='130001')
w3 = wm.Window(background='223322')
w4 = wm.Window(background='443344', foreground='aa0000')
f1.addwidget(w3)
f1.addwidget(w4)
m.root.addwidget(w1)
m.root.addwidget(w2)
m.root.addwidget(f1)
m.background()
#w4.put('1 w4')
#w4.put('2 w4')
#w4.put('3 w4')
#w4.put('4 w4')
#w4.put('({},{}) {}x{}'.format(w4.column, w4.row, w4.height, w4.width))

IO.setraw()

#texto = IO.readshow(w1)
#w2.put(texto + ': ' )
w2.put('entrada: ')
back = 0
while (c := IO.readchar()) != 'q':
	if c.isprintable():
		w1.put('{} -> {}'.format(c, ord(c)))
		w2.modify(lambda x: x + c)
	else:
		w1.put(ord(c))
		if ord(c) == 127:
			back += 1
			w2.modify(lambda x: x[:-back] + ' ' * back if len(x) > back else x)
		#w1.put('{} -> {} {}x{}'.format(c, ord(c), w1.height, w1.width))

IO.unsetraw()
m.die()

print('\033[2J\033[1;1H', end='')
