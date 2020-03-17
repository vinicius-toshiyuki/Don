import termwin as tw
from termwin.controlwindow import ControlWindow, Window
from time import sleep

tw.setraw()

m = tw.Manager()
log = Window(background='222222')
scr = ControlWindow(background='222222')
m.root.addwidget(log)
m.root.addwidget(scr)

log.print('Starting screen')
scr.start()
sleep(5)
log.print('Pausing screen')
scr.pause()
sleep(5)
log.print('Resuming screen')
scr.resume()
sleep(5)
scr.stop()
log.print('Ending')

tw.unsetraw()
m.die()
