import termwin as tw
import termwin.io as io
from termwin.loopwindow import LoopWindow
m = tw.Manager()
w = LoopWindow(timeout=1, background='555555')
m.root.addwidget(w)
io.setraw()

io.output = w
s = io.read('escreve: ')
io.write(s)

import time
time.sleep(2)

m.die()
io.unsetraw()
