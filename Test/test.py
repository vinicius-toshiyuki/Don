import Widget.Manager as wm
from Widget import Io, Prompt

m = wm.Manager()
w1 = wm.Window(timeout=5, background='223322')
w2 = wm.Window(weight=2, background='443344')
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

Io.setraw()
Prompt.wprompt = w3
Prompt.winput = w4
a = Prompt.prompt('Opção', ('essa', 'outra', 'tres', 'quatro'))
w1.put(a)
#Io.output = w2
#Io.write('escreve: ')
#a = Io.read()
#Io.write('o que foi escrito é: ' + a + '\n')
#a = Io.read()

#while (txt := Io.read()) != 'fim':
#	if txt == 'w1':
#		Io.output = w1
#	elif txt == 'w3':
#		Io.output = w3
#	elif txt == 'w4':
#		Io.output = w4
#	else:
#		Io.output = w2
#	Io.write('escrevendo na '+ txt +'\n')
#	Io.output = w2
#	Io.write('escreve: ')
#texto = Io.readshow(w1)
#w2.put(texto + ': ' )
#w2.put('entrada: ')
#back = 0
#while (c := Io.readchar()) != 'q':
#	if c.isprintable():
#		w1.put('{} -> {}'.format(c, ord(c)))
#		w2.modify(lambda x: x + c)
#	else:
#		w1.put(ord(c))
#		if ord(c) == 127:
#			back += 1
#			w2.modify(lambda x: x + '\b')
#	w3.put(str(w2))
			#w2.modify(lambda x: x[:-back] + ' ' * back if len(x) > back else x)
		#w1.put('{} -> {} {}x{}'.format(c, ord(c), w1.height, w1.width))

Io.unsetraw()
m.die()

print('\033[2J\033[1;1H', end='')
print(a)
